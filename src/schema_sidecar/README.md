# schema-sidecar

Two [Agent Skills](https://agentskills.io) that give any repository a [LinkML](https://linkml.io) data model: one schema file from which JSON Schema, Pydantic models, OWL, SHACL, TypeScript and a documentation site are generated.

- **linkml-sidecar** lays down a [linkml-project-copier](https://github.com/linkml/linkml-project-copier) project, at the root of an empty repository or as a `.linkml/` sidecar beside the code of any other.
- **linkml-author** turns its dummy schema into the real model and keeps it generated, documented and tested.

The package also carries the template linkml-sidecar lays down, at the version the skill pins, and the scaffold checks that copy against the pin before it uses it.

## Install the skills

```bash
uvx schema-sidecar skills install --scope user
```

With no `--agent`, the skills go where GitHub Copilot reads them. Name another agent, or a folder:

```bash
uvx schema-sidecar skills install --agent claude-code --scope user
uvx schema-sidecar skills install --agent codex --scope project
uvx schema-sidecar skills install --dest path/to/skills
```

`schema-sidecar skills list` names the skills, `schema-sidecar skills path` prints their folder for `gh skill install --from-local` or `npx skills add`, and `schema-sidecar skills status` says whether the copies an agent reads are this release's.

Then ask your agent to add a LinkML schema to the repository.

## More

- Documentation: <https://w3id.org/lmodel/schema-sidecar/>
- Source and issues: <https://github.com/lmodel/schema-sidecar>
