#!/usr/bin/env python3
"""Export completed/partial raw runs to the permitted small artifact formats."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def package(run,out):
    out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((run/"manifest.json").read_text())
    snapshots={}
    for name,expected in manifest["sources"].items():
        data=(run/"source"/name).read_bytes()
        if hashlib.sha256(data).hexdigest()!=expected:
            raise ValueError("Snapshot changed: "+name)
        snapshots[name]=data.decode("utf-8")
    (out/"sources.json").write_text(json.dumps(snapshots,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    for name in ("manifest.json","status.json"):
        shutil.copy2(run/name,out/name)
    if (out/"rows").exists():
        raise ValueError("Refusing to overwrite published receipts")
    shutil.copytree(run/"rows",out/"rows")
    for name in ("plan.json","seeds.csv"):
        source=run/"source"/manifest["registration"]["directory"]/name
        shutil.copy2(source,out/name)
    from summarize import summarize
    return summarize(run,out)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(package(args.run.resolve(),args.out.resolve()),indent=2))
