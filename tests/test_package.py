"""The schema-sidecar package on PyPI carries the skills unchanged, with the template, installs them, and checks them.

pyproject.toml builds a wheel that holds skills/ and .claude-plugin/ beside
the `schema-sidecar` command (src/schema_sidecar/cli.py), and inside
linkml-sidecar the template scripts/carry-template.py wrote. A person at a
site that reaches only a package index installs the skills with that
command, so it has to earn the trust the other installers have:

- every file of both skills, and nothing else, byte for byte, with each
  script's executable bit;
- the folder each agent reads, at each scope, the project's being the
  repository's top folder, and a folder given by hand;
- one skill or both, and a refusal of a name the package does not carry;
- an earlier copy replaced whole, so a file the new release dropped is gone;
- a plain message, not a traceback, when a folder cannot be written;
- a status that tells this package's copy from a changed one, and reads a
  copy `gh skill install` rewrote, or one installed from GitHub without the
  template, as the same release;
- the standard library alone, on Python 3.9, the oldest Python the package
  claims;
- a build from the hashes .pypi/requirements.txt holds that makes the
  same bytes twice, into a folder holding the two files pypi.yml expects,
  with the template and its record in linkml-sidecar's assets/.

The command tests run the command from this checkout, where it finds the
skills in the repository. The wheel tests build the package with uv from a
local clone of the pinned template, and are skipped where either is missing.
"""

from __future__ import annotations

import ast
import filecmp
import json
import os
import shutil
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from conftest import REPO, load_scaffold_module, pin, template_src

SRC = REPO / "src"
SKILLS = sorted(p.parent.name for p in (REPO / "skills").glob("*/SKILL.md"))
CONSTRAINTS = REPO / ".github" / "pypi" / "requirements.txt"
ASSETS = "skills/linkml-sidecar/assets/"


def command(*args: str, cwd: Path | None = None, home: Path | None = None, python: list[str] | None = None):
    env = dict(os.environ, PYTHONPATH=str(SRC))
    if home is not None:
        env["HOME"] = str(home)
        env["USERPROFILE"] = str(home)
    return subprocess.run(
        [*(python or [sys.executable]), "-m", "schema_sidecar", *args],
        cwd=cwd or REPO,
        env=env,
        capture_output=True,
        text=True,
    )


def tracked(*paths: str) -> list[str]:
    out = subprocess.run(["git", "ls-files", "-s", *paths], cwd=REPO, capture_output=True, text=True, check=True)
    return [line for line in out.stdout.splitlines() if line]


def tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def as_gh_installs(skill_md: str, ref: str) -> str:
    """A SKILL.md as `gh skill install` leaves it: the keys sorted, a quote
    YAML does not need dropped, a metadata block naming the source, and no
    blank line after the frontmatter."""
    lines = skill_md.splitlines()
    end = lines.index("---", 1)
    head = {}
    for line in lines[1:end]:
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("'") and ": " not in value and "#" not in value:
            value = value[1:-1].replace("''", "'")
        head[key] = value
    head["metadata"] = f"\n    github-path: skills/x\n    github-ref: {ref}\n    github-tree-sha: {'0' * 40}"
    rows = [f"{key}:{value}" if key == "metadata" else f"{key}: {value}" for key, value in sorted(head.items())]
    body = "\n".join(lines[end + 1 :]).lstrip("\n")
    return "\n".join(["---", *rows, "---", body]) + "\n"


def test_the_two_skills_are_what_the_package_carries():
    assert SKILLS == ["linkml-author", "linkml-sidecar"]


def test_list_names_each_skill_with_its_first_sentence():
    run = command("skills", "list")
    assert run.returncode == 0, run.stderr
    rows = [line.split("\t") for line in run.stdout.splitlines()]
    assert [name for name, _ in rows] == SKILLS
    for name, summary in rows:
        assert summary.endswith((".", ":")), (name, summary)
        assert "''" not in summary, (name, summary)


def test_skills_with_no_action_lists_them():
    run = command("skills")
    assert run.returncode == 0, run.stderr
    assert run.stdout == command("skills", "list").stdout


def test_path_prints_the_skills_and_the_marketplace():
    assert command("skills", "path").stdout.strip() == str(REPO / "skills")
    marketplace = Path(command("skills", "path", "--marketplace").stdout.strip())
    assert (marketplace / ".claude-plugin" / "marketplace.json").is_file()
    assert (marketplace / "skills" / "linkml-sidecar" / "SKILL.md").is_file()


def test_install_copies_every_skill_byte_for_byte_with_its_modes(tmp_path):
    dest = tmp_path / "skills"
    run = command("skills", "install", "--dest", str(dest))
    assert run.returncode == 0, run.stderr
    assert "Installed 2 skills" in run.stdout
    expected = {}
    for line in tracked("skills"):
        mode, _, _, path = line.split(maxsplit=3)
        expected[path[len("skills/") :]] = mode
    assert sorted(tree(dest)) == sorted(expected)
    for rel, mode in expected.items():
        assert (dest / rel).read_bytes() == (REPO / "skills" / rel).read_bytes(), rel
        executable = bool((dest / rel).stat().st_mode & stat.S_IXUSR)
        if os.name != "nt":
            assert executable == (mode == "100755"), rel


@pytest.mark.parametrize(
    ("agent", "scope", "folder"),
    [
        ("github-copilot", "user", ".copilot/skills"),
        ("claude-code", "user", ".claude/skills"),
        ("codex", "user", ".agents/skills"),
        ("github-copilot", "project", ".agents/skills"),
        ("claude-code", "project", ".claude/skills"),
        ("codex", "project", ".agents/skills"),
    ],
)
def test_install_uses_each_agents_folder(tmp_path, agent, scope, folder):
    home, project = tmp_path / "home", tmp_path / "project"
    home.mkdir()
    (project / ".git").mkdir(parents=True)
    (project / "sub").mkdir()
    run = command("skills", "install", "--agent", agent, "--scope", scope, cwd=project / "sub", home=home)
    assert run.returncode == 0, run.stderr
    root = home if scope == "user" else project
    assert sorted(p.name for p in (root / folder).iterdir()) == SKILLS


def test_install_with_no_agent_uses_copilots_folder(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    run = command("skills", "install", "--scope", "user", home=home)
    assert run.returncode == 0, run.stderr
    assert (home / ".copilot" / "skills" / "linkml-author" / "SKILL.md").is_file()


def test_install_one_skill_and_refuse_an_unknown_one(tmp_path):
    dest = tmp_path / "skills"
    run = command("skills", "install", "--dest", str(dest), "--skill", "linkml-author")
    assert run.returncode == 0, run.stderr
    assert [p.name for p in dest.iterdir()] == ["linkml-author"]
    bad = command("skills", "install", "--dest", str(dest), "--skill", "ktl-docent")
    assert bad.returncode == 2
    assert "no skill named ktl-docent" in bad.stderr


def test_install_refuses_both_dest_and_scope_and_neither(tmp_path):
    both = command("skills", "install", "--dest", str(tmp_path), "--scope", "user")
    assert both.returncode == 2 and "not both" in both.stderr
    neither = command("skills", "install")
    assert neither.returncode == 2 and "name the scope" in neither.stderr


def test_install_replaces_an_earlier_copy_whole(tmp_path):
    dest = tmp_path / "skills"
    old = dest / "linkml-sidecar"
    (old / "references").mkdir(parents=True)
    (old / "references" / "dropped.md").write_text("gone in this release\n")
    run = command("skills", "install", "--dest", str(dest))
    assert run.returncode == 0, run.stderr
    assert not (old / "references" / "dropped.md").exists()
    assert not [p for p in dest.iterdir() if p.name.startswith(".")]


@pytest.mark.skipif(os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0), reason="needs a folder this user cannot write")
def test_an_unwritable_folder_gives_a_plain_message(tmp_path):
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(0o500)
    try:
        run = command("skills", "install", "--dest", str(locked / "skills"))
    finally:
        locked.chmod(0o700)
    assert run.returncode == 1
    assert run.stderr.startswith("schema-sidecar: ") and "Traceback" not in run.stderr


def test_status_tells_a_changed_copy_from_this_packages(tmp_path):
    dest = tmp_path / "skills"
    assert command("skills", "install", "--dest", str(dest)).returncode == 0
    same = command("skills", "status", "--dest", str(dest))
    assert same.returncode == 0, same.stdout
    assert same.stdout.count("same as this package") == 2
    (dest / "linkml-author" / "references" / "metamodel.md").write_text("changed\n")
    changed = command("skills", "status", "--dest", str(dest))
    assert changed.returncode == 1
    assert "differs from this package in 1 file (references/metamodel.md)" in changed.stdout


@pytest.mark.skipif(os.name == "nt", reason="Windows keeps no executable bit")
def test_status_reports_a_lost_executable_bit(tmp_path):
    dest = tmp_path / "skills"
    assert command("skills", "install", "--dest", str(dest)).returncode == 0
    (dest / "linkml-sidecar" / "scripts" / "linkml-scaffold.sh").chmod(0o644)
    run = command("skills", "status", "--dest", str(dest))
    assert run.returncode == 0
    assert "1 script lost the executable bit" in run.stdout


def test_status_reads_a_gh_rewrite_as_the_same_release(tmp_path):
    dest = tmp_path / "skills"
    assert command("skills", "install", "--dest", str(dest)).returncode == 0
    skill_md = dest / "linkml-sidecar" / "SKILL.md"
    skill_md.write_text(as_gh_installs(skill_md.read_text(encoding="utf-8"), "refs/tags/v0.6.0"), encoding="utf-8")
    run = command("skills", "status", "--dest", str(dest))
    assert run.returncode == 0, run.stdout
    assert "installed by gh skill from v0.6.0" in run.stdout


def test_status_reads_a_copy_without_the_template_as_the_same_release(tmp_path, monkeypatch):
    """A package that carries the template, and a copy installed from GitHub, which does not."""
    root = tmp_path / "package"
    shutil.copytree(REPO / "skills", root / "skills", ignore=shutil.ignore_patterns("__pycache__"))
    (root / "skills" / "linkml-sidecar" / "assets" / "linkml-project-copier").mkdir(parents=True)
    (root / "skills" / "linkml-sidecar" / "assets" / "linkml-project-copier" / "copier.yaml").write_text("x: 1\n")
    (root / "skills" / "linkml-sidecar" / "assets" / "linkml-project-copier.json").write_text("{}\n")
    monkeypatch.syspath_prepend(str(SRC))
    from schema_sidecar import cli

    installed = tmp_path / "installed"
    shutil.copytree(REPO / "skills" / "linkml-sidecar", installed / "linkml-sidecar", ignore=shutil.ignore_patterns("__pycache__"))
    changed, lost, no_template = cli.compare(installed / "linkml-sidecar", root / "skills" / "linkml-sidecar")
    assert (changed, lost, no_template) == ([], [], True)


def test_status_with_nothing_installed_says_so(tmp_path):
    home, project = tmp_path / "home", tmp_path / "project"
    home.mkdir()
    (project / ".git").mkdir(parents=True)
    run = command("skills", "status", cwd=project, home=home)
    assert run.returncode == 0
    assert "Neither skill is in" in run.stdout


def test_the_command_uses_the_standard_library_alone():
    allowed = set(sys.stdlib_module_names) | {"schema_sidecar", "__future__"}
    for path in (SRC / "schema_sidecar").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [node.module or ""]
            for name in names:
                assert name.split(".")[0] in allowed, (path.name, name)


uv = shutil.which("uv")
needs_uv = pytest.mark.skipif(uv is None, reason="uv is not installed")


def build(out: Path, source: Path) -> None:
    """Build as pypi.yml does, from the build backend at the hashes .pypi/requirements.txt holds."""
    subprocess.run(
        [uv, "build", "--quiet", "--build-constraints", str(CONSTRAINTS), "--require-hashes", "--out-dir", str(out), str(source)],
        check=True,
    )


@needs_uv
def test_the_command_runs_on_python_3_9(tmp_path):
    run = command(
        "skills",
        "install",
        "--dest",
        str(tmp_path / "skills"),
        python=[uv, "run", "--no-project", "--python", "3.9", "python"],
    )
    assert run.returncode == 0, run.stderr
    assert sorted(p.name for p in (tmp_path / "skills").iterdir()) == SKILLS


@pytest.fixture(scope="module")
def dist(tmp_path_factory) -> Path:
    """The package built from this checkout, with the template carried from a local clone of the pin."""
    if uv is None:
        pytest.skip("uv is not installed")
    src = template_src()
    if not src or not Path(src, ".git").exists():
        pytest.skip("no local clone of the pinned template (.template-cache/linkml-project-copier)")
    subprocess.run([sys.executable, str(REPO / "scripts" / "carry-template.py"), "--clone", src], check=True, capture_output=True)
    out = tmp_path_factory.mktemp("dist")
    build(out, REPO)
    return out


@pytest.fixture(scope="module")
def wheel(dist) -> Path:
    (built,) = dist.glob("schema_sidecar-*-py3-none-any.whl")
    return built


@needs_uv
def test_the_build_folder_holds_the_two_files_pypi_yml_expects(dist):
    (wheel_file,) = dist.glob("*.whl")
    version = wheel_file.name.split("-")[1]
    shown = sorted(p.name for p in dist.iterdir() if not p.name.startswith("."))
    assert shown == [f"schema_sidecar-{version}-py3-none-any.whl", f"schema_sidecar-{version}.tar.gz"]


@needs_uv
def test_a_second_build_makes_the_same_bytes(dist, tmp_path):
    build(tmp_path, REPO)
    for file in dist.iterdir():
        if not file.name.startswith("."):
            assert filecmp.cmp(file, tmp_path / file.name, shallow=False), file.name


@needs_uv
def test_the_wheel_carries_the_skills_plugin_and_template_and_nothing_else(wheel):
    with zipfile.ZipFile(wheel) as z:
        members = {i.filename: i for i in z.infolist() if not i.filename.endswith("/")}
        record = json.loads(z.read(f"schema_sidecar/{ASSETS}linkml-project-copier.json"))
    package = {name for name in members if name.startswith(("schema_sidecar/skills/", "schema_sidecar/.claude-plugin/"))}
    carried = {name for name in package if name.startswith(f"schema_sidecar/{ASSETS}")}
    expected = {}
    for line in tracked("skills", ".claude-plugin"):
        mode, _, _, path = line.split(maxsplit=3)
        expected["schema_sidecar/" + path] = mode
    assert package - carried == set(expected)
    for name, mode in expected.items():
        wheel_mode = (members[name].external_attr >> 16) & 0o777
        assert bool(wheel_mode & stat.S_IXUSR) == (mode == "100755"), name
    code = {name for name in members if name.startswith("schema_sidecar/") and name not in package}
    assert code == {"schema_sidecar/README.md", "schema_sidecar/__init__.py", "schema_sidecar/__main__.py", "schema_sidecar/cli.py"}
    ref, sha = pin()
    assert (record["ref"], record["commit"], record["source"]) == (ref, sha, "gh:linkml/linkml-project-copier")
    assert f"schema_sidecar/{ASSETS}linkml-project-copier/copier.yaml" in carried


@needs_uv
def test_the_installed_wheel_installs_skills_whose_scaffold_trusts_the_template(dist, tmp_path):
    venv = tmp_path / "venv"
    subprocess.run([uv, "venv", "--quiet", "--python", "3.9", str(venv)], check=True)
    bin_dir = venv / ("Scripts" if os.name == "nt" else "bin")
    python = bin_dir / ("python.exe" if os.name == "nt" else "python")
    (wheel_file,) = dist.glob("*.whl")
    subprocess.run([uv, "pip", "install", "--quiet", "--no-index", "--python", str(python), str(wheel_file)], check=True)
    dest = tmp_path / "skills"
    exe = bin_dir / ("schema-sidecar.exe" if os.name == "nt" else "schema-sidecar")
    run = subprocess.run([str(exe), "skills", "install", "--dest", str(dest)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    paths = [line.split(maxsplit=3)[3][len("skills/") :] for line in tracked("skills")]
    installed = sorted(rel for rel in tree(dest) if not rel.startswith("linkml-sidecar/assets/"))
    assert installed == sorted(paths)
    for rel in paths:
        assert (dest / rel).read_bytes() == (REPO / "skills" / rel).read_bytes(), rel
    status = subprocess.run([str(exe), "skills", "status", "--dest", str(dest)], capture_output=True, text=True)
    assert status.returncode == 0, status.stdout + status.stderr
    assets = dest / "linkml-sidecar" / "assets"
    record = json.loads((assets / "linkml-project-copier.json").read_text(encoding="utf-8"))
    assert load_scaffold_module().tree_id(assets / "linkml-project-copier") == record["tree"]
