---
type: Explanation
id: https://w3id.org/lmodel/schema-sidecar/knowledge/explanation/beside-a-ktl-bundle
title: Beside a KTL bundle
description: "How the skills treat a host that carries a .lokf/ Knowledge Trust Ladder bundle: the bundle is KTL's and neither skill writes there, the schema imports nothing from it, the skills take a schema as far as a published release, and ktl-librarian adapts published schemas into the bundle's domain vocabulary; also how an older sidecar tied to a bundle moves to the plain layout."
genre: explanation
resource: docs/architecture.md
tags:
  - ktl
  - lokf
  - domain vocabulary
  - lokf adapt
  - publishing
about:
  - https://w3id.org/lmodel/schema-sidecar/knowledge/glossary/domain-schema
  - https://w3id.org/lmodel/schema-sidecar/knowledge/glossary/domain-vocabulary
references:
  - https://w3id.org/lmodel/schema-sidecar/knowledge/references/knowledge-trust-ladder
  - https://w3id.org/lmodel/schema-sidecar/knowledge/references/publishing
  - https://w3id.org/lmodel/schema-sidecar/knowledge/references/schema-layouts
sources:
  - resource: docs/architecture.md
  - resource: README.md
  - resource: skills/linkml-sidecar/SKILL.md
  - resource: skills/linkml-author/SKILL.md
  - resource: skills/linkml-sidecar/references/layouts.md
generated:
  by: process:ktl-librarian
  at: "2026-11-13T22:30:17Z"
status: draft
---

# Overview

A [Knowledge Trust Ladder (KTL)](https://w3id.org/ktl/) bundle, `.lokf/`, belongs to KTL, which maintains it. Neither skill writes there, and the project is the same with or without a bundle: its schema imports nothing from `.lokf/`.

The skills take a schema as far as a published release: a tag, and the merged file that `just merged` writes in a project linkml-sidecar made. A bundle takes the schema once it is published. Its domain vocabulary may draw on several published schemas, from this repository or any other, or on none, and ktl-librarian builds it with `lokf adapt`.

## What linkml-author does beside a bundle

linkml-author never creates, edits or regenerates a file under `.lokf/`, and never runs a recipe that writes there, unless the person names the file and asks. Its hand-off says which file there the person named, if any, and that ktl-librarian adapts a published release into the bundle's vocabulary.

A `project.justfile` that carries `lokf-adapt` recipes, from an older linkml-sidecar, is the host's own. The skills run those recipes only when the person asks.

## An older sidecar beside a bundle

Up to 0.5.2, linkml-sidecar connected a sidecar to a KTL bundle itself, in one of three forms:

- The schema imports LOKF core, as up to 0.4.x.
- The schema sits in `.lokf/schema/`, as in 0.5.0.
- `project.justfile` carries `lokf-adapt` recipes, as from 0.5.1.

The preflight's `lokf` line warns about the first two, and linkml-author shows the person the move in `references/layouts.md` before any edit. Each form moves to the plain layout on the project's side. The bundle's side is KTL's: after either of the first two moves, `.lokf/justfile` may still name the project's own file, and ktl-librarian's domain-vocabulary page says what it names instead.
