"""The scaffold with the template the schema-sidecar package carries in assets/.

The fast tests run a copy of the skill with the fake copier against a small
template whose pin each test sets.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import pytest

from conftest import FACTS, FAKE_COPIER, REPO, SIDECAR, Git, bash, have, load_scaffold_module, make_host, pin, read, run, template_src, write

CARRY = REPO / "scripts" / "carry-template.py"


def template_repo(root: Path) -> tuple[Path, str]:
    """A git repository with nested folders, a name that sorts apart from a folder, and an executable file."""
    write(root / "copier.yaml", "_subdirectory: template\n")
    write(root / "template" / "README.md.jinja", "# {{ project_name }}\n")
    write(root / "a.b", "a file whose name sorts before a/ as a folder\n")
    write(root / "a" / "c.txt", "inside a/\n")
    write(root / "a-b" / "deep" / "x", "deeper\n")
    script = write(root / "scripts" / "run.sh", "#!/bin/sh\necho run\n")
    script.chmod(0o755)
    git = Git(root)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "template")
    return root, git("rev-parse", "HEAD").strip()


def carry(skill: Path, repo: Path, commit: str, ref: str = "v9.9.9") -> dict:
    """Copy repo into skill/assets/ with its record, as carry-template.py does."""
    files = skill / "assets" / "linkml-project-copier"
    shutil.copytree(repo, files, ignore=shutil.ignore_patterns(".git"))
    (files / "empty-folder").mkdir()
    record = {
        "source": "gh:linkml/linkml-project-copier",
        "copied_from": "https://example.invalid/linkml-project-copier.git",
        "ref": ref,
        "commit": commit,
        "tree": Git(repo)("rev-parse", "HEAD^{tree}").strip(),
    }
    write(skill / "assets" / "linkml-project-copier.json", json.dumps(record, indent=2) + "\n")
    return record


@pytest.fixture
def carried(tmp_path):
    """A copy of linkml-sidecar that carries a small template, and its record."""
    repo, commit = template_repo(tmp_path / "template")
    skill = tmp_path / "skill"
    shutil.copytree(SIDECAR, skill, ignore=shutil.ignore_patterns("__pycache__"))
    record = carry(skill, repo, commit)
    return skill, record


def scaffold_from(skill: Path, host: Path, record: dict, env: dict | None = None, unset=("LINKML_TEMPLATE_SRC",)):
    full = dict(FACTS)
    full["LINKML_COPIER"] = f"{sys.executable} {FAKE_COPIER}"
    full["LINKML_TEMPLATE_REF"] = record["ref"]
    full["LINKML_TEMPLATE_SHA"] = record["commit"]
    full.update(env or {})
    return run(["bash", skill / "scripts" / "linkml-scaffold.sh", "--host", host], env=full, unset=unset)


def test_tree_id_is_gits_for_every_shape_of_folder(tmp_path):
    repo, _ = template_repo(tmp_path / "template")
    copy = tmp_path / "copy"
    shutil.copytree(repo, copy, ignore=shutil.ignore_patterns(".git"))
    (copy / "empty").mkdir()
    (copy / "a" / "__pycache__").mkdir()
    write(copy / "a" / "__pycache__" / "c.cpython-312.pyc", "bytecode")
    assert load_scaffold_module().tree_id(copy) == Git(repo)("rev-parse", "HEAD^{tree}").strip()


@pytest.mark.skipif(os.name == "nt", reason="Windows keeps no executable bit")
def test_tree_id_sees_a_lost_executable_bit(tmp_path):
    repo, _ = template_repo(tmp_path / "template")
    copy = tmp_path / "copy"
    shutil.copytree(repo, copy, ignore=shutil.ignore_patterns(".git"))
    (copy / "scripts" / "run.sh").chmod(0o644)
    assert load_scaffold_module().tree_id(copy) != Git(repo)("rev-parse", "HEAD^{tree}").strip()


def test_a_carried_template_is_used_with_no_network_and_no_tag(carried, tmp_path):
    skill, record = carried
    host = make_host(tmp_path / "host")
    result = scaffold_from(skill, host, record)
    assert result, result.out
    assert "template carried in this skill (copied from https://example.invalid/linkml-project-copier.git) at v9.9.9" in result.out
    assert f"pin verified offline: the carried template is v9.9.9 ({record['commit'][:12]}), tree {record['tree'][:12]}" in result.out
    assert "ls-remote" not in result.out
    copier_line = next(line for line in result.out.splitlines() if " copier copy " in line or "fake_copier.py copy" in line)
    assert "--vcs-ref" not in copier_line
    assert str(skill / "assets" / "linkml-project-copier") in copier_line


def test_the_answers_name_the_template_and_the_pin_as_a_clones_would(carried, tmp_path):
    skill, record = carried
    host = make_host(tmp_path / "host")
    assert scaffold_from(skill, host, record)
    lines = read(host / ".linkml" / ".copier-answers.yml").splitlines()
    assert lines[0].startswith("#")
    assert lines[1:3] == ["_commit: v9.9.9", "_src_path: gh:linkml/linkml-project-copier"]
    assert sum(line.startswith(("_commit:", "_src_path:")) for line in lines) == 2


def test_a_changed_file_in_the_carried_template_stops_the_run(carried, tmp_path):
    skill, record = carried
    write(skill / "assets" / "linkml-project-copier" / "template" / "README.md.jinja", "# changed\n")
    host = make_host(tmp_path / "host")
    result = scaffold_from(skill, host, record)
    assert result.rc == 2, result.out
    assert f"are not the tree {record['tree'][:12]} of v9.9.9" in result.out
    assert not (host / ".linkml").exists()


def test_an_added_file_in_the_carried_template_stops_the_run(carried, tmp_path):
    skill, record = carried
    write(skill / "assets" / "linkml-project-copier" / "template" / "extra.jinja", "added\n")
    result = scaffold_from(skill, make_host(tmp_path / "host"), record)
    assert result.rc == 2, result.out


def test_a_record_for_another_pin_stops_the_run(carried, tmp_path):
    skill, record = carried
    host = make_host(tmp_path / "host")
    result = scaffold_from(skill, host, record, env={"LINKML_TEMPLATE_REF": "v9.9.8"})
    assert result.rc == 2, result.out
    assert "the template this skill carries is v9.9.9" in result.out and "the pin names v9.9.8" in result.out
    result = scaffold_from(skill, host, record, env={"LINKML_TEMPLATE_SHA": "0" * 40})
    assert result.rc == 2, result.out
    assert not (host / ".linkml").exists()


@pytest.mark.parametrize("text", ["not json", "[]", '{"ref": "v9.9.9"}'])
def test_a_broken_record_stops_the_run(carried, tmp_path, text):
    skill, record = carried
    write(skill / "assets" / "linkml-project-copier.json", text)
    result = scaffold_from(skill, make_host(tmp_path / "host"), record)
    assert result.rc == 2, result.out
    assert "reinstall the schema-sidecar package" in result.out


def test_a_record_without_the_template_stops_the_run(carried, tmp_path):
    skill, record = carried
    shutil.rmtree(skill / "assets" / "linkml-project-copier")
    result = scaffold_from(skill, make_host(tmp_path / "host"), record)
    assert result.rc == 2, result.out


def test_a_source_named_by_hand_wins_over_the_carried_copy(carried, tmp_path):
    skill, record = carried
    write(skill / "assets" / "linkml-project-copier.json", "not json")
    host = make_host(tmp_path / "host")
    result = scaffold_from(
        skill,
        host,
        record,
        env={"LINKML_TEMPLATE_SRC": "gh:linkml/linkml-project-copier", "LINKML_TEMPLATE_SKIP_PIN_CHECK": "1"},
        unset=(),
    )
    assert result, result.out
    assert "template gh:linkml/linkml-project-copier at v9.9.9" in result.out
    assert "--vcs-ref v9.9.9" in result.out


def test_the_repository_carries_no_template(tmp_path):
    """A clone of this repository has no assets/, so the scaffold fetches the template."""
    assert not (SIDECAR / "assets").exists()
    host = make_host(tmp_path / "host")
    result = bash(
        SIDECAR / "scripts" / "linkml-scaffold.sh",
        "--host",
        host,
        "--dry-run",
        env={**FACTS, "LINKML_COPIER": f"{sys.executable} {FAKE_COPIER}", "LINKML_TEMPLATE_SKIP_PIN_CHECK": "1"},
    )
    assert result, result.out
    ref, _ = pin()
    assert f"template gh:linkml/linkml-project-copier at {ref}" in result.out
    assert f"--vcs-ref {ref}" in result.out


@pytest.mark.skipif(not have("git"), reason="git is not installed")
def test_carry_template_writes_the_pinned_template_and_its_record(tmp_path):
    src = template_src()
    if not src or not Path(src, ".git").exists():
        pytest.skip("no local clone of the pinned template (.template-cache/linkml-project-copier)")
    out = tmp_path / "carried"
    result = run([sys.executable, CARRY, "--clone", src, "--out", out])
    assert result, result.out
    ref, sha = pin()
    record = json.loads(read(out / "linkml-project-copier.json"))
    assert record == {
        "commit": sha,
        "copied_from": "a local clone",
        "ref": ref,
        "source": "gh:linkml/linkml-project-copier",
        "tree": Git(Path(src))("rev-parse", f"{sha}^{{tree}}").strip(),
    }
    assert (out / "linkml-project-copier" / "copier.yaml").is_file()
    assert not (out / "linkml-project-copier" / ".git").exists()
    assert load_scaffold_module().tree_id(out / "linkml-project-copier") == record["tree"]


@pytest.mark.slow
def test_the_real_copier_lays_the_same_sidecar_from_the_carried_template(tmp_path):
    """A sidecar from the carried copy matches one from the clone, except the answers' _src_path."""
    src = template_src()
    if src is None or not Path(src, ".git").exists():
        pytest.fail("no template clone: clone the pinned tag into .template-cache/linkml-project-copier")
    if not have("uv"):
        pytest.fail("uv not installed")
    skill = tmp_path / "skill"
    shutil.copytree(SIDECAR, skill, ignore=shutil.ignore_patterns("__pycache__"))
    assert run([sys.executable, CARRY, "--clone", src, "--out", skill / "assets"])
    ref, sha = pin()
    record = json.loads(read(skill / "assets" / "linkml-project-copier.json"))
    carried_host, cloned_host = make_host(tmp_path / "carried"), make_host(tmp_path / "cloned")
    result = run(["bash", skill / "scripts" / "linkml-scaffold.sh", "--host", carried_host], env=FACTS, unset=("LINKML_TEMPLATE_SRC",))
    assert result, result.out
    assert f"pin verified offline: the carried template is {ref} ({sha[:12]}), tree {record['tree'][:12]}" in result.out
    assert run(
        ["bash", SIDECAR / "scripts" / "linkml-scaffold.sh", "--host", cloned_host],
        env={**FACTS, "LINKML_TEMPLATE_SRC": src, "LINKML_TEMPLATE_SKIP_PIN_CHECK": "1"},
    )
    carried_files = {p.relative_to(carried_host).as_posix(): p for p in sorted((carried_host / ".linkml").rglob("*")) if p.is_file()}
    cloned_files = {p.relative_to(cloned_host).as_posix(): p for p in sorted((cloned_host / ".linkml").rglob("*")) if p.is_file()}
    assert sorted(carried_files) == sorted(cloned_files)
    answers = ".linkml/.copier-answers.yml"
    for rel, path in carried_files.items():
        if rel != answers:
            assert path.read_bytes() == cloned_files[rel].read_bytes(), rel
    carried_answers = read(carried_files[answers]).splitlines()
    cloned_answers = read(cloned_files[answers]).splitlines()
    assert [line for line in carried_answers if not line.startswith("_src_path:")] == [line for line in cloned_answers if not line.startswith("_src_path:")]
    assert "_src_path: gh:linkml/linkml-project-copier" in carried_answers
