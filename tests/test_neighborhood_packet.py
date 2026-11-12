"""Offline regressions for sparse, deterministically packaged scientific evidence."""

import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import neighborhood_campaign as campaign
import package_neighborhood_evidence as packet


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


class EvidencePacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.packet = self.base / "packet"

    def stage(self, name):
        root = self.base / "run" / name
        plan = campaign.make_plan(name)
        hashes = {}
        for source in campaign.SOURCES:
            data = f"fixture snapshot for {source}\n".encode()
            write(root / "source" / source, data)
            hashes[source] = sha(data)
        tc = {"compiler": "fixture"}
        manifest = dict(stage=name, model_version=campaign.VERSION, plan=plan,
                        plan_sha256=campaign.digest(plan), sources=hashes, toolchain=tc,
                        model_sha256=campaign.digest([campaign.VERSION, hashes, tc]))
        write(root / "manifest.json", packet.json_bytes(manifest))
        trial = next(t for t in plan if t["init"] == "uniform")
        # Exact at initialization is a feasible, if unlikely, trajectory. All
        # other planned rows are deliberately absent, exercising interrupted runs.
        row = dict(trial, attempts=0, sweeps=0, init_evals=trial["n"]+1, comparisons=0,
                   external_replacements=0, external_changes=0, U=0, S=0, exact_sweep=0, front_sweep=0,
                   archive_sweep=0, post_sweep=0, bad_at_U=0, bad_at_S=0, max_error_at_U=0,
                   max_error_at_S=0, endpoint_repairs_own=0, endpoint_repairs_external=0,
                   first_corner_donor=None, wall_seconds=0.01, stop_reason="post_exact",
                   model_sha256=manifest["model_sha256"], plan_sha256=manifest["plan_sha256"])
        row["record_sha256"] = campaign.digest(row)
        write(root / "rows" / (trial["id"]+".json"), packet.json_bytes(row))
        write(root / "status.json", packet.json_bytes(dict(
            stage=name, state="incomplete", reason="wall_budget", planned=len(plan), recorded=1,
            exact_observed=1, post_exact=1, sweep_cap=0)))
        write(root / "events.jsonl", b'{"event":"budget"}\n')
        return root

    def unpack(self, output):
        return subprocess.run([sys.executable, str(SCRIPTS / "package_neighborhood_evidence.py"),
                               "unpack", "--packet", str(self.packet), "--out", str(output)],
                              text=True, capture_output=True, timeout=20)

    def resign_archive(self, index, stage_position, data):
        item = index["stages"][stage_position]
        item.update(bytes=len(data), sha256=sha(data), file=f"{item['stage']}-{sha(data)[:16]}.tar.gz")
        write(self.packet / item["file"], data)
        write(self.packet / "INDEX.json", packet.json_bytes(index))

    def test_sparse_deterministic_pack_and_exact_restoration(self):
        source = self.stage("smoke")
        index = packet.pack([source], self.packet)
        item, = index["stages"]
        self.assertEqual((item["planned"], item["recorded"], item["missing"]),
                         (len(campaign.make_plan("smoke")), 1, len(campaign.make_plan("smoke"))-1))
        archive = (self.packet / item["file"]).read_bytes()
        self.assertEqual(sha(archive), item["sha256"])
        self.assertEqual(packet.pack([source], self.packet), index)
        self.assertEqual((self.packet / item["file"]).read_bytes(), archive)
        target = self.base / "unpacked"
        self.assertEqual(self.unpack(target).returncode, 0)
        expected = {f.relative_to(source): f.read_bytes() for f in source.rglob("*") if f.is_file()}
        actual = {f.relative_to(target / "smoke"): f.read_bytes() for f in (target/"smoke").rglob("*")
                  if f.is_file()}
        self.assertEqual(actual, expected)
        self.assertNotEqual(self.unpack(target).returncode, 0)

    def test_outer_checksum_index_and_inner_validation(self):
        source = self.stage("smoke")
        baseline = packet.pack([source], self.packet)
        item = baseline["stages"][0]
        archive = self.packet / item["file"]
        data = archive.read_bytes()
        archive.write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
        with self.assertRaisesRegex(ValueError, "checksum"):
            list(packet.read_packet(self.packet))
        archive.write_bytes(data)
        bad_index = copy.deepcopy(baseline)
        bad_index["stages"][0]["missing"] = 0
        write(self.packet/"INDEX.json", packet.json_bytes(bad_index))
        with self.assertRaisesRegex(ValueError, "disagrees"):
            list(packet.read_packet(self.packet))
        files = packet.read_stage(source)
        rowname, = [p for p in files if p.startswith("rows/")]
        for mutation, reason in (("source", "checksum"), ("receipt", "digest"),
                                 ("resigned", "accounting"), ("status", "status")):
            with self.subTest(mutation=mutation):
                modified = dict(files)
                if mutation == "source":
                    modified["source/" + campaign.SOURCES[0]] += b"# unrecorded change"
                elif mutation == "status":
                    status = json.loads(modified["status.json"])
                    status["recorded"] = 2
                    modified["status.json"] = packet.json_bytes(status)
                else:
                    row = json.loads(modified[rowname])
                    row["attempts"] = 1
                    if mutation == "resigned":
                        del row["record_sha256"]
                        row["record_sha256"] = campaign.digest(row)
                    modified[rowname] = packet.json_bytes(row)
                self.resign_archive(copy.deepcopy(baseline), 0, packet.compress(modified))
                with self.assertRaisesRegex(ValueError, reason):
                    list(packet.read_packet(self.packet))

    def test_wrong_analyzer_or_premature_complete_status(self):
        source = self.stage("smoke")
        index = packet.pack([source], self.packet)
        index["analysis_sha256"] = "0" * 64
        write(self.packet / "INDEX.json", packet.json_bytes(index))
        with self.assertRaisesRegex(ValueError, "analysis checksum"):
            list(packet.read_packet(self.packet))
        status = json.loads((source / "status.json").read_text())
        status["state"] = "complete"
        write(source / "status.json", packet.json_bytes(status))
        with self.assertRaisesRegex(ValueError, "completion"):
            packet.pack([source], self.packet)

    def test_unsafe_or_duplicate_member_prevents_partial_restore(self):
        sources = [self.stage("smoke"), self.stage("main")]
        base_index = packet.pack(sources, self.packet)
        contents = packet.read_stage(sources[1])
        for kind in ("traversal", "symlink", "duplicate"):
            with self.subTest(kind=kind):
                data = io.BytesIO()
                with tarfile.open(fileobj=data, mode="w:gz") as stream:
                    for key, blob in contents.items():
                        member = tarfile.TarInfo(key)
                        member.size = len(blob)
                        stream.addfile(member, io.BytesIO(blob))
                    member = tarfile.TarInfo("../escape" if kind == "traversal" else "manifest.json")
                    if kind == "symlink":
                        member.type = tarfile.SYMTYPE
                        member.linkname = "../escape"
                    stream.addfile(member)
                self.resign_archive(copy.deepcopy(base_index), 1, data.getvalue())
                destination = self.base / ("restore-" + kind)
                result = self.unpack(destination)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("unsafe or duplicate", result.stderr)
                self.assertFalse(destination.exists(), "earlier stage must not leak into destination")
                self.assertFalse((self.base / "escape").exists())


if __name__ == "__main__":
    unittest.main()
