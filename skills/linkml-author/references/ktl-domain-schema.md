# Beside a KTL bundle: what the author keeps in mind

The authority on the domain schema that `lokf validate --schema` checks is ktl-librarian's [domain-schema.md](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-schema.md). linkml-sidecar's [ktl.md](https://github.com/noelmcloughlin/linkml-sidecar/blob/main/skills/linkml-sidecar/references/ktl.md) says how a sidecar makes the bundle's copy. This page is the author's short form.

## Two things, kept apart

A LinkML project owns its schema, in `.linkml/src/<slug>/schema/` (a sidecar) or `src/<slug>/schema/` (a project at the root). The schema imports nothing from `.lokf/`, so its lint, generators, data tests and published releases are the same with or without a bundle.

KTL owns `.lokf/schema/`. It holds `lokf.yaml`, the pinned copy of LOKF core, and the domain schema that `.lokf/justfile` names, with every file that schema imports. When the bundle's concepts should use a project's classes, the domain schema is a copy of the project's schema that `lokf adapt` writes, or a composite of a few lines that imports `lokf` and the copy. The project may sit in this repository or another; the copy is the same either way.

A `.lokf/` with no copy is a bundle *about* the repository, as in a schema repository that documents itself. Nothing here applies to it until its maintainers decide the bundle should use the schema's classes.

## What the copy does

`lokf adapt` writes a copy that can sit beside `lokf.yaml`. LinkML merges imported names into one namespace without a warning and keeps the last definition, so a raw import would let a schema's own `id`, `name`, `description` or `Person` replace LOKF's. The copy avoids that:

- **The top classes are re-rooted on `Concept`.** By default adapt re-roots each class that has no parent, is not a mixin and carries the schema's identifier. Pass `--root <Class>` (in a sidecar, through `lokf_adapt_flags` in `project.justfile`) for any other class a concept may name. adapt re-roots on `Concept` only, never on a LOKF class such as `Reference` or `Service`.
- **The identifier goes.** LOKF's `id` takes its place, so a class that lists the identifier must descend from a root, or adapt refuses it.
- **A slot whose IRI is one of `Concept`'s folds into it.** A `schema:name` slot folds into `title`, and a `schema:description` slot into `description`.
- **Every other shared name is renamed and keeps its IRI.** A class becomes `<Prefix><Name>`, as `Person` becomes `AcmePerson`, and a slot becomes `<prefix>_<name>`. It never renames an attribute, so a class attribute named like a LOKF slot keeps its name, and may then clash with that slot in a composite's JSON-LD context.
- **The copy's `notes` list every move.** Name the renames and the re-rooted classes in the hand-off: concepts write the copy's names, and the KTL plugins' "Known LOKF types" setting lists the re-rooted classes and their subclasses.

A schema written to [schema-design.md](schema-design.md)'s rules needs few of these moves. The fewer names it shares with LOKF, the fewer renames its concepts carry.

## Keeping it current

- **Edit the project's schema, never the copy.** Run the project's gate, then `just lokf-adapt`, and commit the copy with the change.
- **`just lokf-adapt-check` fails while the copy is stale**, against the schema or against `.lokf/schema/lokf.yaml`. The sidecar's workflow runs it after the tests. Keep the adapt command and its flags in the one recipe, so the check runs what the write ran.
- **When the `lokf` floor moves**, copy the new toolkit's `lokf.yaml` to `.lokf/schema/` and run `lokf-adapt` in the same change.

## What the validator expects

- **Every class is closed.** A concept fails its class on any key the class does not declare. A built-in LOKF class plus one key of your own is not valid: give the project a class that declares the key.
- **`type` names the class exactly**, as the copy names it. A concept of a subclass writes the subclass name, not the parent's; the validator matches concepts against every class at once.
- **A slot that holds a concept holds its whole IRI.** Range such a slot over a class the copy re-roots, and `--check-refs` checks the target.

## After each change

```bash
just --justfile <project>/justfile lint && just --justfile <project>/justfile gen-project && just --justfile <project>/justfile test
just --justfile <project>/justfile lokf-adapt
cd .lokf && just lokf-validate && just lokf-check-refs
```

Then tell the person which classes are new, so the KTL plugins' "Known LOKF types" setting can list them, and which names the copy renamed. Say too whether any concept in the bundle now needs its `type` changed to a class that declares its keys.
