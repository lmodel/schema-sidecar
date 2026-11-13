# Where a LinkML schema lives, and how the skills find it

A LinkML schema can live in any repository. It need not come from linkml-project-copier or its predecessor, linkml-project-cookiecutter, and the folder a project sits in has no fixed name. So linkml-sidecar and linkml-author find the schema by the signals in the table below, never by its folder, and the preflight (`templates/scripts/linkml-preflight.sh`, or the copy a sidecar installs under `.linkml/scripts/`) does the looking. This page is the rule it applies; the scaffold applies the same one in Python.

## The signals, and how long each lasts

| Signal | What it tells | Lifetime |
| --- | --- | --- |
| `.copier-answers.yml` whose `_src_path` names `linkml-project-copier` | a copier project | as long as copier does |
| `config.public.mk` | a project from copier or from the older cookiecutter, which both render it; it names the schema (`LINKML_SCHEMA_NAME`, `LINKML_SCHEMA_SOURCE_DIR`) | a convenience file upstream may retire; when it is gone, the answers' `project_slug` names the schema (`src/<slug>/schema/<slug>.yaml`) |
| a `*.yaml` or `*.yml` file that imports `linkml:types` or names the `linkml:` prefix and has a top-level `classes:`, `slots:`, `enums:`, `types:`, `subsets:` or `imports:` key | a schema on its own | the language's own |

A `.linkml/` directory is a strong sign that LinkML is in use, but not of what it holds: upstream LinkML may name it for configuration files, and the sidecar names it for a whole project. One file tells the two uses apart: `.linkml/.copier-answers.yml` means the sidecar, and anything else in there is left alone. Both uses keep the generators' settings at `.linkml/generators.yaml`: a sidecar renames the template's `config.yaml` to that, and `--repair generators.yaml` moves a root project's file there.

## Where the preflight looks

The candidates, in the order the first match wins: `.linkml/`, the repository root, the directory the preflight was started in, then every directory one level down, hidden or not. A second project found is reported as `also`, and a person says which one is meant.

With no project anywhere, the preflight finds the schema files by content, among what git tracks or would track, or else in the whole tree. It skips the folders that by convention hold copies, fixtures or rendered output: `.git`, `.github`, `.venv`, `node_modules`, `tmp`, `site`, `project`, `docs`, `tests`, `test`, `fixtures`, `templates`, `.lokf` and `.linkml`.

## What each line means for each skill

| The preflight says | linkml-author | linkml-sidecar |
| --- | --- | --- |
| `ok sidecar .linkml/ from <template> at <tag>` | works there | nothing to do; `--repair` rewrites one file |
| `info sidecar <dir>/ is a LinkML schema project`, or `this repository is itself one` | works there, with the project's own recipes | refuses: the project has the toolchain already |
| `info sidecar .linkml/ holds configuration files` | looks on | installs around them; a name both hold is refused, never overwritten |
| `warn sidecar .linkml/ holds <project files> but no answers` | works there if it is a project | refuses until a person says which it is |
| `ok schema <file>` (one or more) | works on the file in place | `--adopt <file>` gives it the toolchain; several files: a person chooses |
| `info authors schema folder <dir>/: <n> people, <m> commits (<names>)`, or `no person, only <k> bot commits` | weighs whether to offer a refactor, by its [schema-design.md](https://github.com/noelmcloughlin/linkml-sidecar/blob/main/skills/linkml-author/references/schema-design.md); the line is a fact, not a verdict | nothing |
| `missing sidecar no LinkML project or schema` | waits for one | installs the sidecar with the dummy |

## Where a new project goes

With no project or schema yet, the scaffold picks the layout by what the folder holds, and the preflight's `layout` line says which:

| The folder | Layout | The schema |
| --- | --- | --- |
| nothing but git's files, a README, a license, and an agent's folders (`.claude/`, `.agents/`, `.github/` without workflows) | `root`: the copier project is the repository, with the template's own README, docs, license and workflows | `src/<slug>/schema/<slug>.yaml` |
| anything else | `sidecar`: the project in `.linkml/`, a `linkml_schema` doorway, the hoisted workflow | `.linkml/src/<slug>/schema/<slug>.yaml` |
| a schema outside any project | `sidecar` with `--adopt` | where it is |

`--layout` overrides the choice. A folder with no git yet counts as empty, and the root project's `just setup` makes the repository. Both layouts keep the generators' settings in `.linkml/generators.yaml`, so at the root `.linkml/` holds that one file.

### The root run

The scaffold runs the same steps at the root, with these differences:

- **Step 4** pre-seeds only the dummy schema, its test and its data. The template's README, docs, license and workflows stand, since the project is the repository.
- **Step 5's answers** name the folder's own license file, or none, and the two switches, `GH_ACTION_PYPI` and `GH_ACTION_DOCS_PREVIEW`.
- **Step 6** patches `mkdocs.yml`, appends the `merged` recipe and moves the generators' settings to `.linkml/generators.yaml`.
- **Step 7** moves the project into the root. A README or license the folder holds is kept, as copier keeps it, and a `.gitignore` gains the template's lines. Any other name both hold stops the run with exit 3 before anything moves.

## How the tools run

Always through the host's own environment, never through a `linkml-lint` or `gen-project` found on the path: the versions the host tested with are the ones that count. The `tools` line names the first that applies: the project's `justfile` (`just --justfile <project>/justfile <recipe>`, or `uvx --from rust-just just` without `just`), its `Makefile` (`make -C <project> <target>`), `uv run` or `poetry run` when the host's `pyproject.toml` names `linkml`, else `uvx --from linkml <tool>` with the version uvx resolved named in the hand-off.

## Adoption

A schema found outside any project can be given the sidecar's toolchain without moving it. `--adopt <file>` installs the sidecar with no dummy, sets the slug from the file's stem and the id from the file, and points `config.public.mk`'s `LINKML_SCHEMA_SOURCE_DIR` at the file's folder, relative to `.linkml/`. Every recipe derives its paths from that one line, so lint, the generators, the docs and the tests read the schema where it is. The file is never moved, copied, linked or edited.

The folder the template expects, `src/<slug>/schema/`, holds a README that says where the schema is, and no data: the host's classes are not the dummy's, so the hand-off asks for one example per class. The file must be `<slug>.yaml`, because the template names the schema after the slug and reads `.yaml`. `--adopt` refuses a file inside `.lokf/`, a KTL knowledge bundle's folder, which KTL maintains.

## An older sidecar beside a KTL bundle

Up to 0.5.2, linkml-sidecar connected a sidecar to a Knowledge Trust Ladder (KTL) bundle itself, in one of three forms. The preflight's `lokf` line warns about the first two. Each moves to the plain layout on the project's side, as below. The bundle's side is KTL's: after either of the first two moves, `.lokf/justfile` may still name the project's own file, and ktl-librarian's [domain-vocabulary.md](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-vocabulary.md) says what it names instead.

- **The schema imports LOKF core**, as up to 0.4.x. Remove the `lokf` import and each `is_a` on a LOKF class, and give the top classes an identifier slot of the schema's own. Delete `.linkml/.linkmllint.yaml` and the `--render-imports` in `config.public.mk`. Move the examples under `tests/data/problem/valid/` to `tests/data/valid/`, as instances without `type`, and run `--repair tests/test_data.py`.
- **The schema sits in `.lokf/schema/`**, as in 0.5.0. Run `git mv .lokf/schema/<slug>.yaml .linkml/src/<slug>/schema/` and delete the `README.md` beside it. Set `LINKML_SCHEMA_SOURCE_DIR="src/<slug>/schema"` in `.linkml/config.public.mk`, set the `target=` line of `project.justfile`'s `linkml-link` recipe to `.linkml/src/<slug>/schema`, and relink `linkml_schema` there. Then follow the first bullet. `--repair` and `--pointers-only` refuse such a sidecar until it is moved.
- **`project.justfile` carries `lokf-adapt` recipes**, as from 0.5.1. They are the host's own now: nothing rewrites them, and the skills run them only when a person asks.
