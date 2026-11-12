"""Serial, analysis-only verification of the round-24 synthesis.

No scientific trajectories, bootstrap draws, numerical solves or source edits.
Run from the bundle with --repo REPO --out NEW_SCRATCH_DIRECTORY.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


def digest(path, kind="file"):
    data = os.readlink(path).encode() if kind == "symlink-text-not-followed" else path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    bundle = Path(__file__).resolve().parent
    out.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                 "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS"):
        env[name] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPYCACHEPREFIX"] = str(out / "pycache")
    start = time.monotonic()
    record = {"started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "python": sys.version, "numerical_threads": 1, "serial": True,
              "scientific_samples": 0, "commands": []}
    follow = Path("research/reports/large-T-20261109/followup")
    commands = [
        ["-m", "unittest", "discover", "-s", "tests", "-v"],
        ["-m", "py_compile", "sim.py", "large.py", "scripts/run_research.py", str(Path(__file__).resolve())],
        [str(follow / "round-0023/verify.py"), "--bundle", str(follow / "round-0023")],
    ]
    for index, command in enumerate(commands):
        then = time.monotonic()
        result = subprocess.run([sys.executable, *command], cwd=repo, env=env,
                                capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        (out / f"command-{index}.log").write_text(output)
        item = {"argv": ["CONFIGURED_PYTHON", *["verify_checkpoint.py" if v == str(Path(__file__).resolve()) else v for v in command]],
                "returncode": result.returncode, "elapsed_seconds": time.monotonic()-then,
                "output_sha256": hashlib.sha256(output.encode()).hexdigest()}
        match = re.search(r"Ran (\d+) tests in ([0-9.]+)s", output)
        if match:
            item.update(tests=int(match[1]), unittest_seconds=float(match[2]),
                        unittest_ok=bool(re.search(r"\nOK\s*$", output)))
        if index == 2 and result.returncode == 0:
            item["certificate_scope"] = json.loads(result.stdout)
        record["commands"].append(item)
        if result.returncode:
            record["status"] = "FAILED"
            (out / "checks.json").write_text(json.dumps(record, indent=2)+"\n")
            raise RuntimeError(f"command {index} failed; see scratch log")

    source = json.loads((bundle / "sources.json").read_text())
    for entry in source["protected_files"]:
        assert digest(repo / entry["path"], entry["kind"]) == (entry["bytes"], entry["sha256"]), entry["path"]
    record["protected_entries_unchanged"] = len(source["protected_files"])
    record["protected_symlink_texts_not_followed"] = sum(e["kind"] != "file" for e in source["protected_files"])
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    record["head"] = head
    assert head == source["head"]

    activation = repo / follow / "activation-20261112T181239Z-84cbf5"
    inventory = json.loads((activation / "RECOVERY.json").read_text())
    copies = [activation / "recovery/round-0020-github-wip",
              activation / "recovery/round-0020-cb372b60"]
    for spec, directory in zip(inventory, copies):
        for entry in spec["files"]:
            assert digest(directory / entry["path"]) == (entry["bytes"], entry["sha256"])
    names = [e["path"] for e in inventory[0]["files"]]
    assert all((copies[0]/name).read_bytes() == (copies[1]/name).read_bytes() for name in names)
    advertised = ["words.csv", "baseline.csv", "phases.csv", "entrances.csv", "branches.csv",
                  "verification.json", "dependency.json", "checks.json", "provenance.json"]
    assert all(not (directory/name).exists() for directory in copies for name in advertised)
    record["recovery"] = {"inventory_entries_verified": 12, "duplicate_files": names,
                          "missing_advertised_wip_files_in_each_copy": advertised,
                          "status": "hash identity only; no inherited verdict"}

    # Links target the eventual round directory. Sibling bundle files are local;
    # ../ links are resolved as though the controller published round-0024.
    virtual = repo / follow / "round-0024"
    links = []
    for path in bundle.glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            target = target.split("#", 1)[0]
            resolved = (virtual / target).resolve() if target.startswith("../") else (bundle / target).resolve()
            assert resolved.is_file(), (path.name, target)
            links.append({"file": path.name, "target": target})
    record["publication_relative_links_verified"] = len(links)
    record["published_round_reports"] = [i for i in range(1,24) if (repo/follow/f"round-{i:04d}/report.md").is_file()]
    assert record["published_round_reports"] == list(range(1,24))
    for path in bundle.iterdir():
        assert path.is_file() and not path.is_symlink(), path
        assert path.suffix in {".md", ".py", ".csv", ".json", ".png"}, path
        assert path.stat().st_size <= 25_000_000, path
    record["elapsed_seconds"] = time.monotonic()-start
    record["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    record["status"] = "PASS"
    (out / "checks.json").write_text(json.dumps(record, indent=2)+"\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
