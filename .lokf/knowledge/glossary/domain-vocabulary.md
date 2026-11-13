---
type: GlossaryTerm
id: https://w3id.org/lmodel/schema-sidecar/knowledge/glossary/domain-vocabulary
title: Domain vocabulary
description: "The schema files a KTL bundle keeps in .lokf/schema/: published, curated vocabulary that ktl-librarian builds with lokf adapt from published schemas of this repository or any other, or from none; the bundle's own, which neither skill writes."
definition: The schema files a KTL bundle keeps in .lokf/schema/, which ktl-librarian builds with lokf adapt from published schemas, or from none.
resource: skills/linkml-author/SKILL.md
tags:
  - domain vocabulary
  - lokf
relatedTo:
  - https://w3id.org/lmodel/schema-sidecar/knowledge/glossary/domain-schema
  - https://w3id.org/lmodel/schema-sidecar/knowledge/explanation/beside-a-ktl-bundle
sources:
  - resource: skills/linkml-author/SKILL.md
  - resource: docs/architecture.md
  - resource: skills/linkml-sidecar/references/layouts.md
generated:
  by: process:ktl-librarian
  at: "2026-11-13T22:30:17Z"
status: draft
---

# Overview

A **domain vocabulary** is a KTL bundle's own schema, in `.lokf/schema/`. linkml-author calls the schema files there published, curated vocabulary. It may draw on several published schemas, from this repository or any other, or on none, and ktl-librarian builds it with `lokf adapt`.

It belongs to KTL. Neither skill writes it, and a domain schema imports nothing from it. ktl-librarian's [domain-vocabulary page](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-vocabulary.md) is the authority on what it holds and what `.lokf/justfile` names.
