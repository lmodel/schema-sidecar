"""The root layout: an empty folder gets the project at its root, the schema in src/<slug>/schema/.

Empty means nothing but git's files, a README, a license and an agent's
folders. The template's own README, docs, license and workflows stand there,
since the project is the repository; the skill adds only the dummy schema,
its test and data, the merged recipe and the generators' settings in
.linkml/generators.yaml. The fast tests run the fake copier; the slow one
runs the real template and its gate.
"""

from __future__ import annotations

import pytest

from conftest import FACTS, PREFLIGHT, SCAFFOLD, Git, add_lokf, bash, have, make_host, matches, pin, read, run, scaffold, template_src, tree, write

MERGED = "linkml-sidecar: the merged schema"
DOORWAY = "linkml-sidecar: the linkml_schema doorway"


def empty_host(tmp_path, **kwargs):
    return make_host(tmp_path, code=False, **kwargs)


def outside_git(root):
    return {k: v for k, v in tree(root).items() if not k.startswith(".git/") and k != ".git"}


def test_an_empty_repository_gets_the_project_at_its_root(tmp_path):
    host = empty_host(tmp_path)
    readme, license_text = read(host / "README.md"), read(host / "LICENSE")
    result = scaffold(host)
    assert result and matches(result.out, r"^scaffold: layout root;"), result.out
    answers = read(host / ".copier-answers.yml")
    assert f"_commit: {pin()[0]}" in answers and matches(answers, r"^existing_license_file: \"?LICENSE\"?$") and "gh_action_pypi: false" in answers
    schema = read(host / "src" / "demo" / "schema" / "demo.yaml")
    assert "id: https://w3id.org/acme/demo\n" in schema and "PersonStatus" in schema
    assert (host / "tests" / "data" / "valid" / "Person-001.yaml").is_file() and (host / "tests" / "test_data.py").is_file()
    # The folder's README and license stand, as copier keeps them.
    assert read(host / "README.md") == readme and read(host / "LICENSE") == license_text
    assert matches(result.out, r"^handoff: kept the folder's own README\.md"), result.out
    # The generators' settings sit where a sidecar's do.
    assert (host / ".linkml" / "generators.yaml").is_file() and not (host / "config.yaml").exists()
    assert "LINKML_GENERATORS_CONFIG_YAML=.linkml/generators.yaml\n" in read(host / "config.public.mk")
    assert sorted(p.name for p in (host / ".linkml").iterdir()) == ["generators.yaml", "scripts"]
    assert (host / ".linkml" / "scripts" / "linkml-preflight.sh").stat().st_mode & 0o111
    project_justfile = read(host / "project.justfile")
    assert project_justfile.count(MERGED) == 1 and DOORWAY not in project_justfile
    assert "site_url: https://acme.github.io/demo/linkml/" in read(host / "mkdocs.yml")
    # No sidecar pieces: no doorway, no aside, no llms.txt, no hoisted workflow.
    assert not (host / "linkml_schema").exists() and not (host / "llms.txt").exists()
    assert not (host / ".github" / "workflows" / "linkml-sidecar.yaml").exists() and (host / ".github" / "workflows" / "main.yaml").is_file()
    assert not list(host.glob(".linkml-staging-*"))
    assert matches(result.out, r"^next: just install && just lint && just test"), result.out


def test_a_folder_without_git_or_a_license_is_told_to_run_just_setup(tmp_path):
    host = empty_host(tmp_path, readme=False, license_file=False, git=False)
    result = scaffold(host)
    assert result, result.out
    assert matches(read(host / ".copier-answers.yml"), r"^existing_license_file: (''|\"\")?$")
    assert read(host / "LICENSE") == "The template's Apache-2.0 license.\n" and read(host / "README.md").startswith("# demo\n")
    assert matches(result.out, r"^handoff: the template wrote LICENSE for Apache-2\.0"), result.out
    assert matches(result.out, r"^next: no git yet: add any agent folder here") and matches(result.out, r"^next: just setup "), result.out


def test_no_license_file_and_the_custom_id_is_refused_at_the_root(tmp_path):
    host = empty_host(tmp_path, license_file=False)
    before = outside_git(host)
    result = scaffold(host, facts={**FACTS, "LICENSE_ID": "LicenseRef-Custom"})
    assert result.rc == 2 and "must be one of its SPDX ids" in result.out, result.out
    assert outside_git(host) == before


def test_a_gitignore_already_there_gains_the_template_s_lines_once(tmp_path):
    host = empty_host(tmp_path)
    write(host / ".gitignore", "node_modules/\n.venv\n")
    assert scaffold(host)
    text = read(host / ".gitignore")
    assert text.startswith("node_modules/\n.venv\n") and "# From linkml-project-copier's .gitignore" in text
    assert "\nproject/\n" in text and text.count(".venv") == 1


def test_a_name_both_hold_stops_the_run_and_nothing_moves(tmp_path):
    host = empty_host(tmp_path)
    write(host / "mkdocs.yml", "site_name: mine\n")
    before = outside_git(host)
    result = scaffold(host, "--layout", "root")
    assert result.rc == 3 and "mkdocs.yml" in result.out and "nothing was written" in result.out, result.out
    assert outside_git(host) == before


def test_another_readme_keeps_the_template_s_readme_out(tmp_path):
    host = empty_host(tmp_path, readme=False)
    write(host / "README.rst", "Demo\n====\n")
    result = scaffold(host)
    assert result and not (host / "README.md").exists() and read(host / "README.rst") == "Demo\n====\n", result.out
    assert matches(result.out, r"^handoff: kept the folder's own README\.rst"), result.out


def test_an_empty_folder_inside_a_repository_is_not_laid_by_itself(tmp_path):
    """A root project there would advise just setup, whose git init nests a repository; the person chooses."""
    make_host(tmp_path / "repo")
    host = tmp_path / "repo" / "schema-project"
    host.mkdir()
    result = scaffold(host)
    assert result.rc == 3 and "inside the repository at" in result.out and not list(host.iterdir()), result.out
    result = scaffold(host, "--layout", "root")
    assert result and (host / ".copier-answers.yml").is_file(), result.out
    assert not matches(result.out, r"^next: just setup") and matches(result.out, r"^handoff: this folder is below its repository's root"), result.out
    other = tmp_path / "repo" / "other"
    other.mkdir()
    pre = bash(PREFLIGHT, str(other))
    assert pre and matches(pre.out, r"^info    layout +the folder is empty but inside a repository"), pre.out


def test_anything_else_in_the_folder_picks_the_sidecar(tmp_path):
    host = make_host(tmp_path)
    result = scaffold(host)
    assert result and matches(result.out, r"^scaffold: layout sidecar;") and (host / ".linkml" / ".copier-answers.yml").is_file(), result.out
    assert not (host / ".copier-answers.yml").exists()


def test_a_github_folder_with_workflows_is_not_empty(tmp_path):
    host = empty_host(tmp_path)
    write(host / ".github" / "workflows" / "ci.yaml", "name: ci\n")
    result = scaffold(host)
    assert result and matches(result.out, r"^scaffold: layout sidecar;"), result.out


@pytest.mark.parametrize("args", [("--adopt", "schema/demo.yaml"), ("--gitignored",)], ids=["adopt", "gitignored"])
def test_sidecar_only_flags_are_refused_with_layout_root(tmp_path, args):
    host = empty_host(tmp_path)
    write(host / "schema" / "demo.yaml", "id: https://w3id.org/acme/demo\nname: demo\nimports:\n  - linkml:types\nclasses: {}\n")
    result = scaffold(host, "--layout", "root", *args)
    assert result.rc == 2 and "are for a sidecar" in result.out, result.out


def test_gitignored_in_an_empty_folder_picks_the_sidecar(tmp_path):
    host = empty_host(tmp_path)
    result = scaffold(host, "--gitignored")
    assert result and matches(result.out, r"^scaffold: layout sidecar;"), result.out


def test_layout_sidecar_overrides_an_empty_folder(tmp_path):
    host = empty_host(tmp_path)
    result = scaffold(host, "--layout", "sidecar")
    assert result and (host / ".linkml" / ".copier-answers.yml").is_file() and not (host / ".copier-answers.yml").exists(), result.out


def test_the_two_switches_turn_on_the_template_s_workflows(tmp_path):
    host = empty_host(tmp_path)
    result = scaffold(host, env={"GH_ACTION_PYPI": "true"})
    assert result, result.out
    assert (host / ".github" / "workflows" / "pypi-publish.yaml").is_file() and not (host / ".github" / "workflows" / "test_pages_build.yaml").exists()
    assert matches(result.out, r"^handoff: PyPI publishing on, the docs preview off"), result.out


def test_a_dry_run_at_the_root_writes_nothing(tmp_path):
    host = empty_host(tmp_path)
    before = outside_git(host)
    result = scaffold(host, "--dry-run")
    assert result and matches(result.out, r"^scaffold: layout root;") and matches(result.out, r"^scaffold:   answer existing_license_file"), result.out
    assert outside_git(host) == before


def test_a_bundle_in_the_folder_is_left_alone_at_the_root_too(tmp_path):
    host = empty_host(tmp_path)
    add_lokf(host)
    before = tree(host / ".lokf")
    result = scaffold(host, "--layout", "root")
    assert result and tree(host / ".lokf") == before, result.out
    assert matches(result.out, r"^handoff: \.lokf/ is a KTL knowledge bundle, which KTL maintains; nothing was written there"), result.out


def test_repair_and_pointers_say_a_root_project_is_no_sidecar(tmp_path):
    host = empty_host(tmp_path)
    assert scaffold(host)
    for args in (("--repair", "README.md"), ("--pointers-only",)):
        result = bash(SCAFFOLD, "--host", str(host), *args, env={"LINKML_TEMPLATE_SKIP_PIN_CHECK": "1"})
        assert result.rc == 3 and "is a schema project at its root, not a sidecar" in result.out, (args, result.out)


@pytest.mark.slow
def test_the_real_template_passes_the_gate_at_the_root(tmp_path):
    src = template_src()
    if src is None:
        pytest.fail("no template clone: set LINKML_TEMPLATE_SRC or clone the pinned tag into .template-cache/linkml-project-copier")
    for tool in ("uv", "just"):
        if not have(tool):
            pytest.fail(f"{tool} not installed")
    host = empty_host(tmp_path)
    result = scaffold(host, env={"LINKML_TEMPLATE_SRC": src}, fake=False)
    assert result, result.out
    assert matches(read(host / ".copier-answers.yml"), r"^existing_license_file: \"?LICENSE\"?$")
    for recipe in ("install", "lint", "test", "site", "merged"):
        done = run(["just", recipe], cwd=host)
        assert done, f"just {recipe} failed:\n{done.out[-3000:]}"
    assert (host / "project" / "linkml" / "demo.yaml").is_file()
    git = Git(host)
    git("add", "-A")
    git("commit", "-q", "-m", "scaffolded")
    update = run(["uvx", "--from", "copier>=9.4.0,<10", "--with", "jinja2-time", "copier", "update", "--trust", "--skip-answered", "--quiet"], cwd=host)
    assert update, update.out[-2000:]
    assert git("status", "--porcelain") == "", "copier update at the same pin changed something"
    assert not (host / "config.yaml").exists(), "copier update brought config.yaml back"
