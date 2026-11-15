#!/usr/bin/env python3
"""Copy linkml-project-copier at the scaffold's pin into carried-template/,
for the schema-sidecar package to carry inside the linkml-sidecar skill.

The scaffold fetches the template from GitHub when it runs. The package
carries it instead, so that a machine which reaches a package index and no
git host can lay down a schema project. pyproject.toml puts what this script
writes into the wheel, as the skill's assets/:

    carried-template/linkml-project-copier/       the template's files
    carried-template/linkml-project-copier.json   where they came from

The pin is read from skills/linkml-sidecar/scripts/linkml-scaffold.sh, the
one place it is held. The files come from a clone at the pinned tag, checked
to be the pinned commit, and are taken from the commit itself, never from a
working tree. Their git tree id is worked out by the scaffold's own
tree_id() and checked against the commit's tree, so the record says what
the scaffold will check, and the scaffold checks what git holds.

    python3 scripts/carry-template.py                  clone from TEMPLATE_URL
    python3 scripts/carry-template.py --clone <path>   use a clone already made

TEMPLATE_URL defaults to the lmodel organisation's copy of the template,
whose tags are upstream's. Standard library only, Python 3.9 or later.
"""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "linkml-sidecar"
DRIVER = SKILL / "scripts" / "linkml-scaffold.sh"
OUT = REPO / "carried-template"
NAME = "linkml-project-copier"
DEFAULT_URL = "https://github.com/lmodel/linkml-project-copier.git"


def scaffold_module():
    spec = importlib.util.spec_from_file_location("linkml_scaffold", SKILL / "scripts" / "linkml-scaffold.py")
    module = importlib.util.module_from_spec(spec)
    # Loading the module would otherwise leave a __pycache__ in skills/, and
    # pypi.yml compares skills/ with what the wheel installs.
    sys.dont_write_bytecode, before = True, sys.dont_write_bytecode
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = before
    return module


def pin() -> tuple[str, str]:
    text = DRIVER.read_text(encoding="utf-8")
    ref = re.search(r'LINKML_TEMPLATE_REF:=(v[0-9]+\.[0-9]+\.[0-9]+)}', text)
    sha = re.search(r'LINKML_TEMPLATE_SHA:=([0-9a-f]{40})}', text)
    if not ref or not sha:
        sys.exit(f"carry-template: no pin in {DRIVER}")
    return ref.group(1), sha.group(1)


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--clone", type=Path, help="a clone of the template that holds the pinned tag")
    parser.add_argument("--out", type=Path, default=OUT, help=f"the folder to write (default: {OUT.relative_to(REPO)})")
    args = parser.parse_args(argv)

    ref, sha = pin()
    url = os.environ.get("TEMPLATE_URL", DEFAULT_URL)
    with tempfile.TemporaryDirectory(prefix="carry-template-") as scratch:
        if args.clone:
            clone = args.clone.resolve()
            # A clone on this machine is named as one, so no local path goes
            # into a package.
            copied_from = "a local clone"
        else:
            clone = Path(scratch) / "clone"
            subprocess.run(["git", "-c", "advice.detachedHead=false", "clone", "--quiet", "--depth", "1", "--branch", ref, url, str(clone)], check=True)
            copied_from = url
        commit = git("rev-parse", f"refs/tags/{ref}^{{commit}}", cwd=clone).stdout.decode().strip()
        if commit != sha:
            sys.exit(f"carry-template: the tag {ref} in {copied_from} names {commit}, not the pinned {sha}")
        expected_tree = git("rev-parse", f"{sha}^{{tree}}", cwd=clone).stdout.decode().strip()

        files = Path(scratch) / "files"
        files.mkdir()
        archive = git("archive", "--format=tar", sha, cwd=clone).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            if hasattr(tarfile, "data_filter"):
                tar.extractall(files, filter="data")
            else:  # pragma: no cover - Python before 3.12 without the backport
                tar.extractall(files)

        tree = scaffold_module().tree_id(files)
        if tree != expected_tree:
            sys.exit(f"carry-template: the files exported from {sha} hash to tree {tree}, and git says {expected_tree}")

        record = {
            "source": scaffold_module().TEMPLATE_SOURCE,
            "copied_from": copied_from,
            "ref": ref,
            "commit": sha,
            "tree": tree,
        }
        out = args.out.resolve()
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        shutil.copytree(files, out / NAME)
        (out / f"{NAME}.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"carry-template: {ref} ({sha[:12]}, tree {tree[:12]}) from {copied_from} into {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
