---
type: GlossaryTerm
id: https://w3id.org/ktl/linkml-sidecar/knowledge/glossary/domain-vocabulary
title: Domain vocabulary
description: The bundle's file in .lokf/schema/ that .lokf/justfile names on its schema := line, with every file it imports; it always imports lokf, lists the classes a concept may name beyond LOKF's own, and lokf validate --schema checks the bundle against it; in KTL mode it is the copy lokf adapt writes from the sidecar's schema.
definition: The file in .lokf/schema/ that .lokf/justfile names on its schema := line, with every file it imports; it always imports lokf, and lists the classes a bundle's concepts may name beyond LOKF's own.
resource: skills/linkml-author/references/ktl-domain-vocabulary.md
tags:
  - domain vocabulary
  - lokf
relatedTo:
  - https://w3id.org/ktl/linkml-sidecar/knowledge/glossary/domain-schema
  - https://w3id.org/ktl/linkml-sidecar/knowledge/explanation/ktl-mode
sources:
  - resource: skills/linkml-author/references/ktl-domain-vocabulary.md
  - resource: skills/linkml-sidecar/references/ktl.md
  - resource: skills/linkml-author/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-11-12T14:47:34Z"
status: draft
---

# Overview

A **domain vocabulary** is the bundle's file: the one `.lokf/justfile` names on its `schema :=` line, with every file it imports, all in `.lokf/schema/` beside LOKF core's copy `lokf.yaml`. It lists the classes a concept may name beyond LOKF's own, and it always imports `lokf`. `lokf validate --schema` checks the bundle against it. Every class is closed, so a concept carries only the slots its class declares, and a concept writes its class name in `type` exactly.

When the bundle's concepts use a LinkML project's classes, the domain vocabulary is a copy `lokf adapt` writes from the project's domain schema, or a composite of a few lines that imports `lokf` and the copy. In KTL mode the scaffold has `lokf adapt` write `.lokf/schema/<slug>.yaml` from the sidecar's schema, and names that copy on the justfile's line and as `[tool.lokf] schema`. `lokf adapt` prints that the copy is a *LOKF domain schema*, the toolkit's name for a domain vocabulary. An adopted schema gets no copy, and the bundle's maintainers decide whether to give it one. A domain vocabulary written for the bundle alone is KTL's file, not a LinkML project's.

ktl-librarian's domain-vocabulary page is the authority on what the validator expects.
