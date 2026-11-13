---
type: Reference
id: https://w3id.org/lmodel/schema-sidecar/knowledge/references/knowledge-trust-ladder
title: Knowledge Trust Ladder
description: The Knowledge Trust Ladder (KTL), whose bundle is a .lokf/ folder in the host; beside one, the scaffold writes a copy of the sidecar's schema to .lokf/schema/<slug>.yaml as the bundle's domain vocabulary, and ktl-librarian's domain-vocabulary page is the authority on what lokf validate expects.
genre: reference
resource: https://w3id.org/ktl
tags:
  - ktl
  - lokf
  - knowledge bundle
sources:
  - resource: README.md
  - resource: docs/architecture.md
  - resource: skills/linkml-sidecar/references/ktl.md
generated:
  by: process:ktl-librarian
  at: "2026-11-12T14:47:34Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
---

# Overview

A [Knowledge Trust Ladder](https://w3id.org/ktl) (KTL) bundle is a `.lokf/` folder in the host. The sidecar stands alone, and beside a KTL bundle the scaffold writes a copy of its schema to `.lokf/schema/<slug>.yaml` with `lokf adapt`. That copy, which `.lokf/justfile` names, is the bundle's domain vocabulary. A schema the host already held (`--adopt`) gets no copy.

ktl-librarian's [domain-vocabulary page](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-vocabulary.md) is the recipe and the authority on what the validator expects. linkml-sidecar's `references/ktl.md` says how the scaffold sets it up.
