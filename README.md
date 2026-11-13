# schema-sidecar

schema-sidecar gives any repository a [LinkML](https://linkml.io) data model: one schema file from which JSON Schema, Pydantic models, OWL, SHACL, TypeScript and a documentation site are generated. Two [Agent Skills](https://agentskills.io) do the work, on the project shape that [linkml-project-copier](https://github.com/linkml/linkml-project-copier) defines.

Documentation is at [w3id.org/lmodel/schema-sidecar](https://w3id.org/lmodel/schema-sidecar/).

## Get started

Install the skills:

```bash
gh skill install lmodel/schema-sidecar --all --scope user
```

Then open your agent in a repository and say, in turn:

1. "Set up a LinkML schema project here."
2. "Model this repository's data in the schema."
3. "Lint, generate and test the schema."

[The install page](https://w3id.org/lmodel/schema-sidecar/docs/install/#quick-start) gives the other ways to install, and [running the scripts without an agent](https://w3id.org/lmodel/schema-sidecar/docs/install/#run-the-scripts-without-an-agent) gives the commands for a person at a shell.

> **Only want to ask?** Install `ktl-docent` into any agent you use, by a route from [the install page](https://w3id.org/ktl/docs/install/), and ask it about this project. It answers from the bundle and says how far each answer has been checked.
>
> **Agents:** if `.lokf/knowledge/index.md` exists, read it first. `llms.txt` says how to weigh it.

## The two skills

| Skill | What it does | Runs |
| --- | --- | --- |
| `linkml-sidecar` | Installs the project from linkml-project-copier at a verified pin, around a dummy schema or a schema the repository already holds, and repairs a file it owns | once |
| `linkml-author` | Turns the dummy into the repository's model, and keeps any LinkML schema linted, generated, documented and tested | often |

## Where the project goes

| The repository | The project | The schema |
| --- | --- | --- |
| empty, or a folder with no git yet | at the root: the repository is the schema project | `src/<slug>/schema/` |
| a codebase | a hidden `.linkml/` sidecar beside the code, outside its build, with a `linkml_schema` link to the schema | `.linkml/src/<slug>/schema/` |
| a schema but no project | a sidecar around that schema, which stays where it is | where it is |

[The architecture](https://w3id.org/lmodel/schema-sidecar/docs/architecture/) says who owns which file, and why the template is trusted only at its pin.

## Beside a knowledge bundle

A [Knowledge Trust Ladder (KTL)](https://w3id.org/ktl/) bundle in `.lokf/` belongs to KTL, and neither skill writes there. A bundle takes a published release of the schema, which ktl-librarian adapts into the bundle's vocabulary.
