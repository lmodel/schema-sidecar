---
type: Reference
id: https://w3id.org/lmodel/schema-sidecar/knowledge/references/knowledge-trust-ladder
title: Knowledge Trust Ladder
description: The Knowledge Trust Ladder (KTL), whose bundle is a .lokf/ folder in the host; it belongs to KTL, neither skill writes there, and a bundle takes a published release of the schema, which ktl-librarian adapts into the bundle's vocabulary.
genre: reference
resource: https://w3id.org/ktl
tags:
  - ktl
  - lokf
  - knowledge bundle
sources:
  - resource: README.md
  - resource: docs/architecture.md
generated:
  by: process:ktl-librarian
  at: "2026-11-13T22:30:17Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
---

# Overview

A [Knowledge Trust Ladder](https://w3id.org/ktl/) (KTL) bundle is a `.lokf/` folder in the host. It belongs to KTL, which maintains it, and neither skill writes there. A bundle takes a published release of the schema, which ktl-librarian adapts into the bundle's vocabulary.

ktl-librarian's [domain-vocabulary page](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-vocabulary.md) says how it builds that vocabulary with `lokf adapt`.
