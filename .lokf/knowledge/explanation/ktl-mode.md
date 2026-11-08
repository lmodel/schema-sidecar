---
type: Explanation
id: https://w3id.org/ktl/linkml-sidecar/knowledge/explanation/ktl-mode
title: KTL mode
description: "What changes when the host carries a .lokf/ Knowledge Trust Ladder bundle: the project's schema stays in .linkml/ and imports nothing from .lokf/, the scaffold pins .lokf/schema/lokf.yaml, adds lokf-adapt recipes, writes the bundle a copy at .lokf/schema/<slug>.yaml and names it in .lokf/justfile and as [tool.lokf] schema; an adopted schema gets no copy."
genre: explanation
resource: skills/linkml-sidecar/references/ktl.md
tags:
  - ktl
  - lokf
  - domain schema
  - lokf validate
  - lokf adapt
about:
  - https://w3id.org/ktl/linkml-sidecar/knowledge/glossary/domain-schema
references:
  - https://w3id.org/ktl/linkml-sidecar/knowledge/references/knowledge-trust-ladder
  - https://w3id.org/ktl/linkml-sidecar/knowledge/playbooks/linkml-author-skill
sources:
  - resource: skills/linkml-sidecar/references/ktl.md
  - resource: skills/linkml-author/references/ktl-domain-schema.md
  - resource: skills/linkml-author/SKILL.md
  - resource: docs/architecture.md
generated:
  by: process:ktl-librarian
  at: "2026-11-08T01:05:25Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T11:13:31Z"
---

# Overview

A LinkML project and a KTL bundle are separate things. When the host carries a `.lokf/` bundle, the preflight switches on KTL mode. The scaffold lays down the same project as in plain mode, with the same `Person` dummy, in `.linkml/src/<slug>/schema/`, and the schema imports nothing from `.lokf/`. The bundle gets a copy: `lokf adapt` (lokf 0.9.0 or later) writes `.lokf/schema/<slug>.yaml` from the project's schema, and `.lokf/justfile` names that copy as the bundle's domain schema.

A schema the host already held (`--adopt`) gets no copy: the scaffold runs in plain mode beside the bundle and says so in the hand-off. A bundle beside a schema may be a bundle *about* the repository, and whether its concepts use the schema's classes is for its maintainers to decide. `--adopt` refuses a file inside `.lokf/`, because a schema there is KTL's.

## What the scaffold does in KTL mode

1. Pins `.lokf/schema/lokf.yaml` when it is absent, out of the installed `lokf` toolkit, at the floor `.lokf/pyproject.toml` names. A copy at the root of `.lokf/`, KTL's layout before 0.62.0, stays in place.
2. Appends `lokf-adapt` and `lokf-adapt-check` to `project.justfile`. The first writes the copy; the second fails while the copy is stale against the schema or against `lokf.yaml`. `lokf_adapt_flags` takes adapt's own flags, such as `--root <Class>`.
3. Writes the copy. `lokf adapt --dry-run` must read the staged dummy before anything moves into `.linkml/`, or the run stops with exit 2. It refuses when `.lokf/schema/<slug>.yaml` already exists.
4. Sets `schema := "schema/<slug>.yaml"` in `.lokf/justfile`. A justfile that already names a schema keeps it, and the hand-off says to import `<slug>` from it.
5. Writes the same path as `[tool.lokf] schema` in `.lokf/pyproject.toml`. A table that names another schema is printed, not patched.

## What the copy holds

The copy imports `lokf`, the file beside it. `lokf adapt` re-roots the schema's top classes on `Concept`, so a concept may name them as its `type`; drops the schema's identifier slot for LOKF's `id`; folds a slot whose IRI is one of `Concept`'s into it, as `name` folds into `title`; and renames any other name LOKF also defines, as `Person` becomes `AcmePerson` for the slug `acme`. The copy's `notes` list each move.

## Keeping the copy current

Edit the schema, never the copy. After each change, run `just lokf-adapt` and commit the copy with it. The sidecar's workflow runs on `.linkml/**` and `.lokf/schema/**` and runs `just lokf-adapt-check` after the tests, so a stale copy fails the gate. When the `lokf` floor moves, copy the new `lokf.yaml` into `.lokf/schema/` and run `lokf-adapt` in the same change.

## What the host still does by hand

It adds each class the copy re-roots on `Concept`, and each subclass, to the *Known LOKF types* setting of the KTL Registrar and KTL Curator plugins. On an older `.lokf/`, it changes each KTL workflow's validate step to run `just lokf-check-refs`. When the sidecar is removed, the copy stays; to remove it too, `git rm` it, reset `schema := ""`, and remove `[tool.lokf] schema`.

## An older KTL-mode sidecar

Up to 0.4.x the schema imported `.lokf/lokf.yaml` and was itself the domain schema; 0.5.0 kept it in `.lokf/schema/<slug>.yaml`. The preflight warns about both, and `references/ktl.md` gives the steps to move either to the copy.
