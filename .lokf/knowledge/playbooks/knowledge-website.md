---
type: Playbook
id: https://w3id.org/lmodel/schema-sidecar/knowledge/playbooks/knowledge-website
title: Knowledge website
description: "How the website in website/ is built, previewed and published: a Hugo site with a page per concept and its trust label, the lokf export files under knowledge/, and the README as its home page, deployed to GitHub Pages by knowledge-website.yaml once KNOWLEDGE_WEBSITE_ENABLED is true."
genre: how-to
resource: website/README.md
tags:
  - website
  - github pages
  - hugo
  - KNOWLEDGE_WEBSITE_ENABLED
references:
  - https://w3id.org/lmodel/schema-sidecar/knowledge/references/knowledge-trust-ladder
sources:
  - resource: website/README.md
  - resource: website/site.toml
  - resource: website/hugo.toml
  - resource: website/scripts/build.sh
  - resource: .github/workflows/knowledge-website.yaml
  - resource: website
generated:
  by: process:ktl-librarian
  at: "2026-11-15T03:16:32Z"
status: draft
---

# Overview

The folder `website/` builds the site that the Knowledge website workflow publishes to GitHub Pages, at `https://lmodel.github.io/schema-sidecar/`. Hugo builds it. Every page comes from a file the repository already holds, so a change to the site is a change to that file.

- Each concept in `.lokf/knowledge/` becomes a page under `knowledge/`, with its trust label from `knowledge-report.sh`, its sources and its relations both ways. The bundle also gives the health page and the graph.
- The four files `lokf export` writes are served under `knowledge/`, beside each concept's own Markdown file and its JSON-LD. The bundle log is served as an Atom feed, `knowledge/log.xml`.
- The README becomes the home page.

The build also looks for `docs/`, the figures in `.assets/`, `CHANGELOG.md` and a LinkML schema, and shows each one it finds. The data is the one part a setting turns on: `browse` in `site.toml` names a folder of SQLite databases.

## Preview it

Preview the site with bash, git and [uv](https://docs.astral.sh/uv/). Run these from `website/`:

```bash
scripts/build.sh          # dist/, with the search index, then checks every link between its pages
scripts/build.sh serve    # http://localhost:1313/schema-sidecar/, rebuilt as you edit
scripts/build.sh preview  # the site as it will be published, at http://localhost:1313/
```

`PORT=1400 scripts/build.sh serve` uses another port. Hugo and Pagefind come from PyPI, at the versions `website/pyproject.toml` names and the hashes `website/uv.lock` holds. `scripts/prepare.sh` runs first. It runs `lokf export` from the toolkit that `.lokf/uv.lock` pins.

## What to edit

- **A page's words:** edit the file it comes from: the README, a page under `docs/`, or a concept. A concept changes through the librarian and the curator like any other change to the bundle.
- **The site's own values:** edit `website/site.toml`: its address, title and description, the repository, and the optional settings. A comment above each says what it takes.
- **Its look:** edit `website/assets/css/custom.css`, which is this repository's own and is loaded last.

Those two files and `website/README.md` are the repository's own. Every other file in `website/` is a copy of the ktl-website skill's template, and the skill's repair replaces it.

## Publishing

`.github/workflows/knowledge-website.yaml` builds the site on a pull request that touches its inputs, with the link check, and deploys nothing. A weekly run rebuilds it from the default branch. The `deploy` job runs for the default branch only, once the repository variable `KNOWLEDGE_WEBSITE_ENABLED` is `true`. Before setting it, tell Pages once to take its site from Actions, under Settings, Pages, Source. Set the variable under Repository variables, not on an environment, because a job's `if:` sees only repository and organization variables.
