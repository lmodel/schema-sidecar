"""The scaffold's pure functions: the facts' validation, the answers file, the slug, the placeholder check, the emptiness rule."""

from __future__ import annotations

import pytest


from conftest import FACTS, load_scaffold_module

mod = load_scaffold_module()


def facts(**changes):
    out = {token: "" for token in mod.TOKENS}
    out.update(FACTS)
    out.update(TEMPLATE_REF="v0.5.0", TODAY="2026-10-07", COPYRIGHT_YEAR="2026", LICENSE_FILE="LICENSE", GH_ACTION_PYPI="false", GH_ACTION_DOCS_PREVIEW="false")
    out.update(changes)
    return out


def test_a_root_project_names_the_folder_s_license_and_its_two_switches():
    text = mod.answers_text(facts(LICENSE_FILE="", GH_ACTION_PYPI="true"))
    assert 'existing_license_file: ""' in text and "gh_action_pypi: true" in text and "gh_action_docs_preview: false" in text
    assert mod.answers_text(facts(LICENSE_FILE="COPYING")).count('existing_license_file: "COPYING"') == 1


def test_a_switch_that_is_not_true_or_false_is_refused():
    with pytest.raises(mod.Refused, match="GH_ACTION_PYPI must be true or false"):
        mod.validate(facts(GH_ACTION_PYPI="yes"))


def test_a_folder_with_git_a_readme_a_license_and_agent_folders_is_empty(tmp_path):
    for name in (".git/HEAD", "README.md", "LICENSE", ".gitignore", ".claude/settings.json", "AGENTS.md", ".github/copilot-instructions.md"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text("x\n")
    assert mod.not_empty(tmp_path) == []
    (tmp_path / ".github" / "workflows").mkdir()
    (tmp_path / "app.py").write_text("x\n")
    assert mod.not_empty(tmp_path) == [".github/", "app.py"]


def test_the_answers_carry_the_facts_and_the_four_fixed_answers():
    text = mod.answers_text(facts())
    assert 'project_name: "demo"' in text
    assert 'full_name: "Test Person"' in text
    assert "add_example: false" in text
    assert "gh_action_pypi: false" in text
    assert "gh_action_docs_preview: false" in text
    assert 'existing_license_file: "LICENSE"' in text


def test_a_value_with_quotes_is_json_quoted():
    text = mod.answers_text(facts(PROJ_DESC='A "quoted" host: it\'s fine'))
    assert 'project_description: "A \\"quoted\\" host: it\'s fine"' in text


@pytest.mark.parametrize(
    ("change", "needle"),
    [
        ({"PROJ_NAME": "-bad"}, "PROJ_NAME"),
        ({"PROJ_SLUG": "Bad-Slug"}, "PROJ_SLUG"),
        ({"LICENSE_ID": "WTFPL"}, "LICENSE_ID"),
        ({"EMAIL": "nobody"}, "EMAIL"),
        ({"SCHEMA_ID": "https://github.com/acme/demo"}, "code host"),
        ({"SCHEMA_ID": "w3id.org/acme/demo"}, "http(s)"),
        ({"PROJ_DESC": ""}, "PROJ_DESC is not set"),
        ({"COPYRIGHT_YEAR": "26"}, "COPYRIGHT_YEAR"),
    ],
)
def test_a_bad_fact_is_refused_with_its_name(change, needle):
    with pytest.raises(mod.Refused) as caught:
        mod.validate(facts(**change))
    assert caught.value.code == 2 and needle in str(caught.value)


def test_the_slug_is_a_python_package_name():
    assert mod.slugify("Acme Platform") == "acme_platform"
    assert mod.slugify("my-awesome-schema") == "my_awesome_schema"
    assert mod.slugify("42 things") == "schema_42_things"


def test_render_substitutes_every_token_and_refuses_a_leftover():
    assert mod.render("<PROJ_NAME> at <SCHEMA_ID>", facts()) == "demo at https://w3id.org/acme/demo"
    with pytest.raises(mod.Refused, match="SCHEMA_SRC"):
        mod.render("<SCHEMA_SRC>/x.yaml", facts())
    assert mod.render("<slug> and <PROJ_SLUG>", facts()) == "<slug> and demo"


def test_the_template_url_forms():
    assert mod.template_url("gh:linkml/linkml-project-copier") == "https://github.com/linkml/linkml-project-copier.git"
    assert mod.template_url("/a/local/clone") == "/a/local/clone"
