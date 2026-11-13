---
type: GlossaryTerm
id: https://w3id.org/lmodel/schema-sidecar/knowledge/glossary/domain-schema
title: Domain schema
description: A LinkML schema that models a domain, owned by a LinkML project in .linkml/src/<slug>/schema/ or src/<slug>/schema/; it never imports lokf, and a bundle uses its classes through the copy lokf adapt writes into .lokf/schema/, the bundle's domain vocabulary.
definition: A LinkML schema that models a domain and that a LinkML project owns; it never imports lokf.
resource: skills/linkml-sidecar/references/ktl.md
tags:
  - domain schema
  - lokf
sources:
  - resource: skills/linkml-sidecar/references/ktl.md
  - resource: skills/linkml-author/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-11-12T14:47:34Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
---

# Overview

A **domain schema** is a LinkML schema that models a domain, and a LinkML project owns it: in `.linkml/src/<slug>/schema/` in a sidecar, or in `src/<slug>/schema/` in a project at the root. The sidecar's schema is the repository's domain schema. It never imports `lokf`, so its lint, generators, data tests and published releases are the same with or without a KTL bundle.

A bundle uses a domain schema's classes through a copy: `lokf adapt` reads the domain schema and writes the bundle's domain vocabulary into `.lokf/schema/`. Edit the schema, never the copy; no step writes the schema from the bundle. A `.lokf/` with no copy is a bundle *about* the repository: an adopted schema gets no copy, and the bundle's maintainers decide whether to give it one.
