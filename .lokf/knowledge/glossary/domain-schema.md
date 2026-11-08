---
type: GlossaryTerm
id: https://w3id.org/ktl/linkml-sidecar/knowledge/glossary/domain-schema
title: Domain schema
description: A LinkML schema that imports LOKF's core schema so its is_a Concept classes become types a .lokf/ bundle's concepts may carry, checked by lokf validate --schema; it sits in .lokf/schema/ and .lokf/justfile names it, and in KTL mode it is the copy lokf adapt writes from the sidecar's schema.
definition: A LinkML schema importing LOKF's core schema, whose classes that are is_a Concept the bundle's concepts may name in type, checked by lokf validate --schema.
resource: skills/linkml-sidecar/references/ktl.md
tags:
  - domain schema
  - lokf
sources:
  - resource: skills/linkml-sidecar/references/ktl.md
  - resource: skills/linkml-author/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T01:26:03Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
---

# Overview

A **domain schema** is a LinkML schema importing LOKF's, whose `is_a: Concept` classes the bundle's concepts may name in `type`, checked by `lokf validate --schema`. Every class is closed, so a concept carries only the slots its class declares, and a concept writes its class name in `type` exactly.

A domain schema sits in `.lokf/schema/`, beside LOKF core's copy `lokf.yaml`, and `.lokf/justfile` names it (`schema :=`). In KTL mode it is a copy `lokf adapt` writes from the sidecar's schema, which stays in `.linkml/` and imports nothing from `.lokf/`. A bundle beside any other schema does not make it one: an adopted schema gets no copy, and its maintainers decide whether to give it one. ktl-librarian's domain-schema page is the authority on what the validator expects.
