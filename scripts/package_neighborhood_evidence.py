#!/usr/bin/env python3
"""Freeze stage receipts for Git and restore a verified evidence packet for reanalysis."""
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile
import tempfile

from neighborhood_campaign import SOURCES, STAGES, VERSION, digest, make_plan, validate_row

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"[0-9a-f]{20}")
META = {"manifest.json", "status.json", "events.jsonl"}
SOURCE_NAMES = {"source/" + name for name in SOURCES}
INDEX_NAME = "INDEX.json"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(data):
    return (json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def permitted(name):
    path = PurePosixPath(name)
    return (name in META or name in SOURCE_NAMES
            or (len(path.parts) == 2 and path.parts[0] == "rows"
                and path.suffix == ".json" and ID.fullmatch(path.stem)
                and name == str(path)))


def check(stage, files):
    if stage not in STAGES or any(not permitted(path) for path in files):
        raise ValueError("unrecognized stage or archive member")
    if "manifest.json" not in files or "status.json" not in files:
        raise ValueError("missing manifest or stage status")
    manifest = json.loads(files["manifest.json"])
    plan = make_plan(stage)
    if (manifest["stage"] != stage or manifest["model_version"] != VERSION
            or manifest["plan"] != plan or manifest["plan_sha256"] != digest(plan)):
        raise ValueError(f"invalid frozen design for {stage}")
    if set(manifest["sources"]) != set(SOURCES):
        raise ValueError("unexpected scientific source set")
    for name, expected in manifest["sources"].items():
        if sha(files[f"source/{name}"]) != expected:
            raise ValueError(f"source checksum mismatch: {name}")
    if manifest["model_sha256"] != digest([VERSION, manifest["sources"], manifest["toolchain"]]):
        raise ValueError("invalid model signature")
    design = {row["id"]: row for row in plan}
    rows = []
    for name, body in files.items():
        if not name.startswith("rows/"):
            continue
        identity = PurePosixPath(name).stem
        if identity not in design:
            raise ValueError(f"unplanned receipt: {identity}")
        row = json.loads(body)
        validate_row(row, design[identity], manifest)
        rows.append(row)
    status = json.loads(files["status.json"])
    counts = {"planned": len(plan), "recorded": len(rows),
              "post_exact": sum(r["post_sweep"] is not None for r in rows),
              "sweep_cap": sum(r["post_sweep"] is None for r in rows),
              "exact_observed": sum(r["exact_sweep"] is not None for r in rows)}
    state = status.get("state")
    if state not in {"complete", "incomplete", "gate_blocked", "running"} or (
            state == "complete" and len(rows) != len(plan)):
        raise ValueError("stage status is inconsistent with completion")
    if status.get("stage") != stage or any(status.get(k) != v for k, v in counts.items()):
        raise ValueError("stage status disagrees with durable receipts; stop the worker and resume before packaging")
    return {"stage": stage, "planned": len(plan), "recorded": len(rows),
            "missing": len(plan) - len(rows), "status": status["state"],
            "plan_sha256": manifest["plan_sha256"], "model_sha256": manifest["model_sha256"]}


def read_stage(directory):
    names = sorted(META | SOURCE_NAMES)
    names += sorted("rows/" + p.name for p in (directory / "rows").glob("*.json"))
    files = {}
    for name in names:
        path = directory / name
        if name == "events.jsonl" and not path.exists():
            continue
        if path.is_symlink() or not path.is_file() or directory.resolve() not in path.resolve().parents:
            raise ValueError(f"missing or unsafe evidence input: {name}")
        files[name] = path.read_bytes()
    return files


def compress(files):
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0) as compressed:
        with tarfile.open(mode="w|", fileobj=compressed) as archive:
            for name, data in sorted(files.items()):
                member = tarfile.TarInfo(name)
                member.size = len(data)
                member.mode = 0o644
                archive.addfile(member, io.BytesIO(data))
    return buffer.getvalue()


def atomic_file(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        try:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
            handle.close()
            os.replace(tmp, path)
        finally:
            tmp.unlink(missing_ok=True)


def pack(directories, out):
    out.mkdir(parents=True, exist_ok=True)
    stages = [p.name for p in directories]
    if len(set(stages)) != len(stages) or not set(stages) <= set(STAGES):
        raise ValueError("use one folder per recognized stage")
    # Content-addressed files keep the previous index valid until the final atomic swap.
    index = {"format": 1, "analysis_sha256": sha((ROOT / "scripts/analyze_neighborhood_campaign.py").read_bytes()), "stages": []}
    for directory in directories:
        files = read_stage(directory)
        info = check(directory.name, files)
        data = compress(files)
        checksum = sha(data)
        filename = f"{directory.name}-{checksum[:16]}.tar.gz"
        atomic_file(out / filename, data)
        index["stages"].append(dict(info, file=filename, sha256=checksum, bytes=len(data)))
    atomic_file(out / INDEX_NAME, json_bytes(index))
    referenced = {s["file"] for s in index["stages"]}
    for path in out.glob("*.tar.gz"):
        if re.fullmatch(r"(smoke|calibrate|main|holdout)-[0-9a-f]{16}\.tar\.gz", path.name) and path.name not in referenced:
            path.unlink()
    return index


def read_packet(packet):
    index = json.loads((packet / INDEX_NAME).read_bytes())
    if index.get("format") != 1 or not index.get("stages"):
        raise ValueError("unrecognized or empty packet")
    if index.get("analysis_sha256") != sha((ROOT / "scripts/analyze_neighborhood_campaign.py").read_bytes()):
        raise ValueError("analysis checksum mismatch; check out the analysis revision that accompanied this packet")
    visited = set()
    for item in index["stages"]:
        stage = item["stage"]
        checksum = item["sha256"]
        if (stage in visited or stage not in STAGES or not re.fullmatch(r"[0-9a-f]{64}", checksum)
                or item["file"] != f"{stage}-{checksum[:16]}.tar.gz"):
            raise ValueError("invalid packet index entry")
        visited.add(stage)
        data = (packet / item["file"]).read_bytes()
        if len(data) != item["bytes"] or sha(data) != checksum:
            raise ValueError("evidence archive checksum mismatch")
        files = {}
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            for member in archive:
                if not member.isfile() or not permitted(member.name) or member.name in files:
                    raise ValueError("unsafe or duplicate archive member")
                files[member.name] = archive.extractfile(member).read()
        info = check(stage, files)
        if any(item.get(k) != v for k, v in info.items()):
            raise ValueError("evidence index disagrees with archive")
        yield stage, files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    write = sub.add_parser("pack")
    write.add_argument("--runs", type=Path, nargs="+", required=True)
    write.add_argument("--out", type=Path, required=True)
    for action in ("verify", "unpack"):
        read = sub.add_parser(action)
        read.add_argument("--packet", type=Path, required=True)
        if action == "unpack":
            read.add_argument("--out", type=Path, required=True, help="new destination directory")
    args = parser.parse_args()
    if args.action == "pack":
        index = pack(args.runs, args.out)
        print(json.dumps(index["stages"], indent=2))
    elif args.action == "verify":
        print("Verified", ", ".join(stage for stage, _ in read_packet(args.packet)))
    else:
        if args.out.exists():
            parser.error("--out must be a new directory")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=args.out.parent) as temp:
            staging = Path(temp) / "restored"
            for stage, files in read_packet(args.packet):
                for name, data in files.items():
                    dest = staging / stage / name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(data)
            staging.rename(args.out)
        print("Restored", args.out)


if __name__ == "__main__":
    main()
