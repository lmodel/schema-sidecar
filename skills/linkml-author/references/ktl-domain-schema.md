# Beside a KTL bundle: what the author keeps in mind

The authority for a domain schema that `lokf validate --schema` checks is ktl-librarian's [domain-schema.md](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-schema.md). linkml-sidecar's [ktl.md](https://github.com/noelmcloughlin/linkml-sidecar/blob/main/skills/linkml-sidecar/references/ktl.md) says how the sidecar sets one up. This page is the author's short form, and applies when the schema is the bundle's domain schema: `.lokf/justfile` names it (`schema :=`), the justfile names a copy `lokf adapt` wrote from it, or the schema imports `lokf`, the copy of LOKF core in `.lokf/schema/`. A `.lokf/` beside a schema that is neither is a bundle about the repository, and nothing here applies until its maintainers make the schema the domain schema.

## Two routes: import or adapt

**Import.** A schema written for the bundle sits in `.lokf/schema/`, where KTL keeps every schema file, and imports `lokf`, the copy of LOKF core beside it. Its classes descend from `Concept`. The sidecar's dummy takes this route, and the rest of this page assumes it unless a line says otherwise.

**Adapt.** A schema cannot import `lokf.yaml` when it is also published on its own, for importers that never see LOKF. LinkML merges the two files into one namespace, and a name both define (`id`, `name`, `description`, `version`) keeps one definition without a warning. slsa and gist are such schemas. Leave the published schema, the source, as it is. Let lokf's `adapt` write a copy into `.lokf/schema/` that imports the `lokf.yaml` beside it ([publishing.md](publishing.md) lists its moves), and set `schema := "schema/<slug>.yaml"` in `.lokf/justfile` to name the copy. The preflight's `lokf` line then says `a copy lokf adapt wrote`.

On the adapt route:

- **Edit the source, never the copy.** Run the gate where the source lives, then adapt again. Keep the `lokf adapt` command and its flags in one recipe, and add a second recipe that runs it with `--check`. In CI, `--check` fails when the source or the `lokf` floor has moved and the copy has not. The copy's `notes` record what the flags did, not the flags.
- **The project's own tests stay as they are.** The source does not import LOKF, so `tests/data/valid/`, the generated dataclasses and the lint config need none of the workarounds below. `cd .lokf && just lokf-validate` checks the bundle against the copy.
- **The renamed keys are what a concept writes.** `adapt` renames each slot the source shares with LOKF to `<prefix>_<name>` and keeps its IRI, so a concept writes `slsa_id`, not `id`. The copy's `notes` list every rename; name them in the hand-off for the librarian.
- **A duplicate pair has one half left empty.** Some source slots mean the same as one of LOKF's but carry no IRI that `adapt` can match. Each survives beside LOKF's slot, under its own key or a renamed one: slsa's `slsa_name` beside `title`, and `slsa_description` beside LOKF's `description`. A concept writes LOKF's slot and leaves the other empty. lokf pull request 142 proposes `--fold name=title`, which merges the pair in the copy; once a release carries it, adapt again with the fold.
- **The plugins' types are the re-rooted classes.** The copy's `notes` name the classes `adapt` re-rooted on `Concept`; they and their descendants are the names for the KTL plugins' "Known LOKF types" setting.

## What the validator expects

- **Every class is closed.** A concept fails its class on any key the class does not declare. A built-in LOKF class plus one key of your own is not valid: subclass it and declare the key.
- **`type` names the class exactly.** A concept of a subclass writes the subclass name, not the parent's; the validator matches concepts against every class at once.
- **The import stays.** On the import route, `imports: [linkml:types, lokf]` is how the schema sees `Concept`, `Reference`, `Playbook` and the rest. LinkML resolves the name relative to the schema file, so the schema and the pinned copy stay together in `.lokf/schema/`.

## What to write

```yaml
classes:
  Module:                      # a concept LOKF has no class for
    is_a: Concept
    description: One unit of a degree programme.
    slots: [module_code, ects, semester]
  SourceSnapshotReference:     # a built-in that fits, plus keys it lacks
    is_a: Reference
    description: A reference to a snapshot of a source, with when it was reviewed.
    slots: [source_kind, reviewed_at]
```

A class `is_a: Concept` joins the bundle's concept union, and so does any descendant of it. Subclass a built-in whose meaning fits; give a class of its own to what no built-in describes. A published vocabulary the domain schema needs comes in beside `lokf.yaml` through lokf's `adapt` ([publishing.md](publishing.md)), never by a raw import: its `id`, `type` and `name` would merge silently with LOKF's.

## What the generators cannot do here

These limits apply on the import route, where the project's own schema imports LOKF.

- The generated dataclasses (`src/<slug>/datamodel/<slug>.py`) do not compile beside LOKF, because LOKF's `from` slot is a Python keyword and `gen-python` does not escape it. The example runner at the end of `just test` instantiates every file under `tests/data/valid/` through the same dataclasses. So valid examples live under `tests/data/problem/valid/`, which the runner skips, and `tests/test_data.py` validates the files of both folders with `linkml.validator`, loading the schema through `SchemaView` so the relative import resolves. Counter-examples stay under `tests/data/invalid/`. The Pydantic models compile. linkml 1.12.0 escapes the field name. Move the valid examples to `tests/data/valid/` once a release also loads data that uses `from` (PR 4083).
- `just lint` lints every file in the schema's folder, `lokf.yaml` among them, so LOKF's camelCase slot names, its enum values and two of its prefixes would fail it. The project's `.linkmllint.yaml` excuses exactly LOKF's names and turns `canonical_prefixes` off. Regenerate it when `.lokf/schema/lokf.yaml` changes (in a sidecar, linkml-sidecar `--repair .linkmllint.yaml`). Another schema file in the folder is linted too: excuse its names in the same file.
- `gen-doc` renders LOKF's pages too (`--render-imports`), so the docs site shows the whole vocabulary a concept may use.

## After each change

```bash
just --justfile <project>/justfile lint && just --justfile <project>/justfile gen-project && just --justfile <project>/justfile test
cd .lokf && just lokf-validate && just lokf-check-refs
```

On the adapt route, run the recipe that writes the copy after the first line and before the second, so the bundle is checked against the new copy. Then tell the person which classes are new, so the KTL plugins' "Known LOKF types" setting can list them, and whether any concept in the bundle now needs its `type` changed to a class that declares its keys.
