# Security Policy

*This file is a policy, not a threat model. It says how to report, what this repository releases, and what holds each surface that executes here. The reasoning lives in each workflow's header and in the shared [threat model](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/docs/threat-model.md).*

## Reporting a vulnerability

Use GitHub's [private vulnerability reporting](https://github.com/lmodel/schema-sidecar/security/advisories/new), not a public issue or a pull request. Say which file is affected, how it is exploitable, and whether it reaches an installed skill, the PyPI package or only this repository's automation. One person maintains this repository: expect a first reply in days, not hours, and no bounty.

## Supported versions

**Only the latest release receives fixes.** A security fix is released as a patch and noted in [CHANGELOG.md](CHANGELOG.md).

## What this repository releases

It releases two Agent Skills, `linkml-sidecar` and `linkml-author`, under one tag. `publish.yml` creates the tag and the GitHub Release with `gh skill publish`, in the `release` Environment, and dispatches the knowledge release and `pypi.yml`. `pypi.yml` builds the `schema-sidecar` package from the tag under a read-only token. The package carries the skills and the copier template at the tag the scaffold pins, with a record of its commit and git tree, which the scaffold checks offline before it uses the copy. A second job uploads the package by trusted publishing, holding only `id-token: write`, and only when the repository variable `PYPI_RELEASE_ENABLED` is `true`. It is `false` until the `lmodel` organisation is approved on PyPI. `knowledge-release.yaml` attaches the knowledge bundle as a zip, with its `.sha256` and a build-provenance attestation.

## What executes here

| Surface | What holds it |
| --- | --- |
| `validate.yml` on every pull request, and `knowledge-registrar.yaml` on any that touches `.lokf/`: the contract, the tests and the bundle's checks | Read-only jobs with `persist-credentials: false`; the tests install the versions `tests/requirements.txt` pins. |
| `publish.yml` and `pypi.yml`, which tag, release and upload | Dispatched by hand. The write scopes sit in the `release` Environment, limited to `main`, and the `pypi` Environment, limited to `v*` tags. |
| `semantic-release.yml`, which promotes the changelog | Runs semantic-release with `--dry-run` only, and commits the promoted section itself. |
| `knowledge-website.yaml`, which publishes the site to GitHub Pages | Builds under a read-only token; only its deploy job holds `pages: write` and `id-token: write`, from `main`, once `KNOWLEDGE_WEBSITE_ENABLED` is `true`. |
| `scorecard.yml` and `codeql.yml`, which publish the OpenSSF Scorecard and scan the code | Read-only checkout; only the upload of results can write. |
| `knowledge-librarian.yaml`, `knowledge-sync.yaml` and `.lokf/scripts/`, copies of the `ktl-sidecar` templates | The librarian's agent job holds no write token, the sync runs no agent, and a person merges each pull request. [Prompt-injection guards](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/docs/threat-model.md#prompt-injection-guards). |
| The scaffold, run by an agent in another repository | It checks the carried template's git tree and pin against its record before it uses the copy. |

Every workflow declares `permissions: {}` at the top, pins its actions to commit hashes, and runs harden-runner in audit mode. The repository settings require that pinning, block deletion and force-pushes on `main`, block moving or deleting a `v*` tag, and turn on secret scanning with push protection. Required reviewers on the `release` Environment **are not yet in force**.

## Not covered

- LinkML, its generators and its runtime: report them to [LinkML](https://github.com/linkml/linkml/security).
- linkml-project-copier, the template the scaffold applies: report it to [its maintainers](https://github.com/linkml/linkml-project-copier/issues).
- A compromised runner, upstream action or agent harness. Report a finding in one anyway, with its scope and a reproduction.
