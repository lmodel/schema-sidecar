"""The hoisted workflow template holds what the sidecar needs: every step in .linkml/, pinned actions, a locked install, and a docs job that never touches the host's Pages root."""

from __future__ import annotations

import re

import yaml

import pytest

from conftest import FORGEJO_WORKFLOW, WORKFLOW, have, read, run, write

TEXT = read(WORKFLOW)
DOC = yaml.safe_load(TEXT)
JOBS = DOC["jobs"]


def test_every_action_is_pinned_to_a_commit_with_its_version_beside_it():
    for line in TEXT.splitlines():
        if re.match(r"\s*-?\s*uses:", line):
            assert re.search(r"@[0-9a-f]{40} # v[0-9]+\.[0-9]+\.[0-9]+$", line), line


def test_every_step_runs_in_the_sidecar_and_installs_from_the_lock():
    assert DOC["defaults"]["run"]["working-directory"] == ".linkml"
    for job in JOBS.values():
        for step in job["steps"]:
            if "cache-dependency-glob" in step.get("with", {}):
                assert step["with"]["cache-dependency-glob"] == ".linkml/uv.lock"
    runs = [step["run"] for job in JOBS.values() for step in job["steps"] if "run" in step]
    assert any("uv sync --locked --group dev" in r for r in runs)
    assert any(r.strip() == "just lint" for r in runs) and any(r.strip() == "just test" for r in runs)
    assert not any("gh-deploy" in r or "just deploy" in r or "just setup" in r for r in runs)


def test_it_triggers_on_the_sidecar_and_the_bundle_s_schema_folder():
    triggers = DOC[True] if True in DOC else DOC["on"]
    for event in ("pull_request", "push"):
        assert ".linkml/**" in triggers[event]["paths"] and ".lokf/schema/**" in triggers[event]["paths"]
    assert "workflow_dispatch" in triggers


def test_permissions_are_empty_at_the_top_and_write_only_where_publishing_happens():
    assert DOC["permissions"] == {}
    assert JOBS["lint-and-test"]["permissions"] == {"contents": "read"}
    assert JOBS["docs"]["permissions"] == {"contents": "read"}
    assert JOBS["publish-docs"]["permissions"] == {"contents": "write"}


def test_publishing_is_gated_by_the_variable_and_scoped_to_the_subpath():
    publish = JOBS["publish-docs"]
    assert "vars.LINKML_DOCS_ENABLED == 'true'" in publish["if"] and "pull_request" in publish["if"]
    assert publish["needs"] == "docs"
    pages = [s for s in publish["steps"] if "peaceiris/actions-gh-pages" in s.get("uses", "")]
    assert len(pages) == 1
    # Without keep_files peaceiris replaces destination_dir alone, so the pages
    # of a deleted class go and the host's own site stays.
    assert pages[0]["with"]["destination_dir"] == "linkml" and "keep_files" not in pages[0]["with"]
    artifact = [s for s in JOBS["docs"]["steps"] if "upload-artifact" in s.get("uses", "")]
    assert artifact and artifact[0]["with"]["path"] == ".linkml/site"


def test_it_names_no_branch_and_publishes_from_the_default_branch_only():
    triggers = DOC[True] if True in DOC else DOC["on"]
    assert "branches" not in triggers["push"]
    assert "github.event.repository.default_branch" in JOBS["docs"]["if"]
    assert JOBS["publish-docs"]["needs"] == "docs"


CHECK_STEP = "Check the knowledge bundle's copy of the schema"


def check_step(doc):
    steps = [s for s in doc["jobs"]["lint-and-test"]["steps"] if s.get("name") == CHECK_STEP]
    assert len(steps) == 1, f"no single {CHECK_STEP!r} step"
    return steps[0]["run"]


def test_both_templates_check_the_copy_after_the_tests_with_one_script():
    names = [s.get("name") for s in JOBS["lint-and-test"]["steps"]]
    assert names.index(CHECK_STEP) == names.index("Generate, test and run the examples") + 1
    assert check_step(DOC) == check_step(yaml.safe_load(read(FORGEJO_WORKFLOW)))


@pytest.mark.skipif(not have("just"), reason="just not installed locally")
def test_the_check_runs_the_recipe_only_where_the_sidecar_has_it(tmp_path):
    """Only a sidecar installed beside a KTL bundle has lokf-adapt-check, so the step must pass on every other."""
    script = check_step(DOC)
    write(tmp_path / "justfile", "lint:\n    @echo lint\n")
    result = run(["bash", "-c", script], cwd=tmp_path)
    assert result and "no lokf-adapt-check recipe" in result.out, result.out
    write(tmp_path / "justfile", "lint:\n    @echo lint\nlokf-adapt-check:\n    @echo checked; exit 3\n")
    result = run(["bash", "-c", script], cwd=tmp_path)
    assert result.rc != 0 and "checked" in result.out, result.out
