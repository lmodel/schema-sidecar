# KTL mode: a copy of the schema for the bundle

This page is for the **scaffold** and for whoever reads its KTL hand-off lines. A LinkML project and a KTL bundle are separate things. The project owns its schema, the *domain schema*, in `.linkml/src/<slug>/schema/` (or `src/<slug>/schema/` in a project at the root), and the schema imports nothing from `.lokf/`. KTL keeps the bundle's files in `.lokf/schema/`: LOKF core's copy, `lokf.yaml`, and the *domain vocabulary* that `.lokf/justfile` names, with each file it imports. When the bundle's concepts should use the project's classes, that domain vocabulary is a copy of the domain schema, or a file beside it that imports the copy and `lokf`. ktl-librarian's [domain-schema.md](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-schema.md) is the authority on what the validator expects. This page says how the sidecar makes the copy and keeps it current.

## What the scaffold does in KTL mode

When the host has a `.lokf/` bundle and `--adopt` is not given, the scaffold lays down the same project as in plain mode, with the same dummy. Then it:

1. **Pins `.lokf/schema/lokf.yaml`** when it is absent, out of the installed `lokf` toolkit (`uv sync` in `.lokf/`, then the package's `data/lokf.yaml`), at the floor `.lokf/pyproject.toml` names. This is domain-schema.md's step 1. A copy at the root of `.lokf/`, KTL's layout before 0.62.0, stays in place, and the hand-off names it.
2. **Appends two recipes to `project.justfile`.** `lokf-adapt` runs `lokf adapt` on the project's schema and writes `.lokf/schema/<slug>.yaml`. `lokf-adapt-check` runs the same command with `--check`, which fails while the copy is stale against the schema or against `lokf.yaml`. Both run the `lokf` that `.lokf/` pins, which must be 0.9.0 or later, the first release with `adapt`. `LOKF_CMD` runs another, and `lokf_adapt_flags` takes adapt's own flags, such as `--root <Class>`.
3. **Writes the copy.** Before the sidecar is moved into `.linkml/`, `lokf adapt --dry-run` must read the staged dummy and verify its copy, or the run stops with exit 2. Once the sidecar is in place, the scaffold runs the recipe's command. The scaffold refuses to run when `.lokf/schema/<slug>.yaml` already exists.
4. **Names the copy in `.lokf/justfile`** (domain-schema.md's step 4): `schema := "schema/<slug>.yaml"`. A justfile from before that variable gets the line after `bundle := "knowledge"`, and `--schema` in `lokf-validate` and `lokf-check-refs`, which then run from the copy's folder. The edit matches ktl-sidecar's template lines exactly, and a justfile that differs gets the edit printed instead. A justfile that already names a schema keeps it, and the hand-off says to list `<slug>` under that schema's imports, beside `lokf`.
5. **Writes the same path as `[tool.lokf] schema`** in `.lokf/pyproject.toml`, so a `lokf` command given no `--schema` reads the copy too. KTL's preflight warns when the two differ, and so does this sidecar's. A table that already names another schema is printed, not patched.

When the copy cannot be written, steps 4 and 5 are skipped, and the hand-off says to run `just lokf-adapt` and name the copy by hand.

## What the copy holds

The copy imports `lokf`, the file beside it. `lokf adapt` prints that the copy is a *LOKF domain schema*, the toolkit's name for a domain vocabulary. It makes four kinds of move, and the copy's `notes` list each one:

- it re-roots the schema's top classes on `Concept`, so a concept may name them, or a subclass, as its `type`;
- it drops the schema's identifier slot, because LOKF's `id` takes its place;
- it folds a slot whose IRI is one of `Concept`'s into that slot, as the dummy's `name` (`schema:name`) folds into `title`;
- it renames each other name LOKF also defines and keeps its IRI, as the dummy's `Person` becomes `AcmePerson` when the slug is `acme`.

By default adapt re-roots every class that has no parent, is not a mixin, and carries the identifier: the dummy's `NamedThing`. A real schema often needs `--root` for each class a concept may name. adapt re-roots on `Concept` only, never on a LOKF class such as `Reference` or `Service`.

## Keeping the copy current

Edit the schema, never the copy. After each schema change, run `just --justfile .linkml/justfile lokf-adapt` and commit the copy with the change. Step 5's workflow runs on changes to `.linkml/**` and `.lokf/schema/**`, and runs `just lokf-adapt-check` after the tests, so a stale copy fails the gate. When the `lokf` floor moves, copy the new toolkit's `lokf.yaml` to `.lokf/schema/` and run `lokf-adapt` in the same change.

## What the host still does by hand

- **The plugins.** KTL Registrar and KTL Curator each carry a *Known LOKF types* setting. Add each class the copy re-roots on `Concept`, and each of its subclasses, as the copy names them (domain-schema.md, step 5). The skills need no telling: ktl-librarian's Rule 3 reads the schema the justfile names.
- **The workflows of an older `.lokf/`.** On a `.lokf/` from before ktl-sidecar's `schema` variable, the three KTL workflows (`knowledge-registrar.yaml`, `knowledge-librarian.yaml`, `knowledge-release.yaml`) run `uv run lokf validate --check-refs` inline in `.lokf/`. The hand-off asks that each workflow's validate step run `uvx --from rust-just==1.47.0 just lokf-check-refs` instead, so the recipes stay in one place. The runners have no `just`, so the step runs it through `uvx`.
- **Removal.** Removing the sidecar leaves the copy in `.lokf/schema/`, where the justfile still names it, but nothing writes it again. To remove it as well, `git rm` it, reset the justfile's line to `schema := ""` (on an older justfile, both validate recipes to `uv run lokf validate {{ bundle }}`), and remove `[tool.lokf] schema` from `.lokf/pyproject.toml`. `.lokf/schema/lokf.yaml` may stay.

## An adopted schema, and a bundle added later

A schema the host already held (`--adopt`) gets no copy. The scaffold runs in plain mode beside the bundle and says so. A bundle beside a schema may be a bundle *about* the repository, and whether its concepts use the schema's classes is for the bundle's maintainers to decide. `--adopt` refuses a file inside `.lokf/`, because a schema there is KTL's.

When the maintainers want a copy, or when a bundle arrives after the sidecar, `--repair project.justfile` adds the two recipes. Then `just lokf-adapt` writes the copy, and the justfile's `schema :=` line and `[tool.lokf] schema` name it.

## An older KTL-mode sidecar

Earlier releases' KTL mode connected the bundle to the project's own schema, and the preflight's `lokf` line warns about both forms it took. Up to 0.4.x the schema stayed in `.linkml/src/<slug>/schema/`, imported `.lokf/lokf.yaml` by its path, and the justfile named it as `../.linkml/src/<slug>/schema/<slug>.yaml`. 0.5.0 kept the schema itself in `.lokf/schema/<slug>.yaml` and pointed `config.public.mk` there, and `--repair` and `--pointers-only` refuse such a sidecar. To move either to the copy:

1. On 0.5.0, run `git mv .lokf/schema/<slug>.yaml .linkml/src/<slug>/schema/` and delete the `README.md` beside it, which says the schema is elsewhere. Set `LINKML_SCHEMA_SOURCE_DIR="src/<slug>/schema"` in `.linkml/config.public.mk`, set the `target=` line of `project.justfile`'s `linkml-link` recipe to `.linkml/src/<slug>/schema`, and relink `linkml_schema` there.
2. Remove the LOKF import from the schema, and each `is_a` on a LOKF class. Give the top classes an identifier slot of the schema's own, or list each as `--root` in `lokf_adapt_flags`.
3. Delete `.linkml/.linkmllint.yaml` and the `--render-imports` in `config.public.mk`. Move the examples under `tests/data/problem/valid/` to `tests/data/valid/`, as instances without `type`, and run `--repair tests/test_data.py`.
4. Run `--repair project.justfile`, then `just lokf-adapt`, and set the justfile's `schema :=` line and `[tool.lokf] schema` to `schema/<slug>.yaml`.
5. Run both gates. Then `git rm .lokf/lokf.yaml`, once nothing imports it.
