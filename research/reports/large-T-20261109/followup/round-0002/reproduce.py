#!/usr/bin/env python3
"""Restore source snapshots and recompute the report without drawing any outcomes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reproduce(bundle,out):
    if out.exists():
        raise ValueError("Use a new replay directory")
    checksums=bundle/"checksums.json"
    if checksums.exists():
        for name,expected in json.loads(checksums.read_text())["files"].items():
            path=Path(name)
            if path.is_absolute() or ".." in path.parts or digest(bundle/path)!=expected:
                raise ValueError("Curated artifact mismatch: "+name)
    manifest=json.loads((bundle/"manifest.json").read_text())
    snapshots=json.loads((bundle/"sources.json").read_text())
    if set(snapshots)!=set(manifest["sources"]):
        raise ValueError("Source inventory differs")
    run=out/"run"
    for name,text in snapshots.items():
        path=Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Unsafe source path")
        data=text.encode("utf-8")
        if hashlib.sha256(data).hexdigest()!=manifest["sources"][name]:
            raise ValueError("Source bytes differ: "+name)
        destination=run/"source"/path
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(data)
    shutil.copy2(bundle/"manifest.json",run/"manifest.json")
    shutil.copy2(bundle/"status.json",run/"status.json")
    shutil.copytree(bundle/"rows",run/"rows")
    from summarize import summarize
    result=summarize(run,out/"report")
    comparisons={}
    for name in ("summary.json","arithmetic.json","trials.csv","cells.csv","phases.csv","results.png"):
        comparisons[name]=digest(bundle/name)==digest(out/"report"/name)
    if not all(comparisons[name] for name in comparisons if name!="results.png"):
        raise ValueError("Recomputed numeric artifact differs")
    # PNG rasterization can vary by Matplotlib/font version; report it separately.
    return dict(**result,byte_identical=comparisons,new_scientific_outcomes=0,
                exact_engine_source=str(run/"source/scripts/neighborhood_sweep.cpp"))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle",type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(reproduce(args.bundle.resolve(),args.out.resolve()),indent=2))
