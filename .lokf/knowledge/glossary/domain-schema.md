---
type: GlossaryTerm
id: https://w3id.org/lmodel/schema-sidecar/knowledge/glossary/domain-schema
title: Domain schema
description: A LinkML schema that models a domain and that a LinkML project owns, in .linkml/src/<slug>/schema/ or src/<slug>/schema/; it imports nothing from .lokf/, and the skills take it as far as a published release, which a KTL bundle may adapt into its domain vocabulary.
definition: A LinkML schema that models a domain and that a LinkML project owns; it imports nothing from .lokf/.
resource: skills/linkml-author/SKILL.md
tags:
  - domain schema
  - lokf
sources:
  - resource: skills/linkml-author/SKILL.md
  - resource: docs/architecture.md
generated:
  by: process:ktl-librarian
  at: "2026-11-13T22:30:17Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
relatedTo:
  - https://w3id.org/lmodel/schema-sidecar/knowledge/glossary/domain-vocabulary
  - https://w3id.org/lmodel/schema-sidecar/knowledge/explanation/beside-a-ktl-bundle
---

# Overview

A **domain schema** is a LinkML schema that models a domain, and a LinkML project owns it. It stays where the project keeps it: in `.linkml/src/<slug>/schema/` in a sidecar, or in `src/<slug>/schema/` in a project at the root. It imports nothing from `.lokf/`.

The skills take a domain schema as far as a published release: a tag, and the merged file that `just merged` writes in a project linkml-sidecar made. A KTL bundle's domain vocabulary may draw on that release, and ktl-librarian builds the vocabulary with `lokf adapt`. No step of either skill writes into `.lokf/`.
