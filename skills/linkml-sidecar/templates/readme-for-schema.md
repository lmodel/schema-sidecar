> **The data model is a sidecar.** `.linkml/` is <PROJ_NAME>'s
> [LinkML](https://linkml.io) schema project: the JSON Schema, Pydantic
> models, OWL and documentation are generated from the schema, and nothing in
> the build depends on them.
> `linkml_schema/` at the root is the schema's folder, `<SCHEMA_FOLDER>/`,
> under a visible name. Edit the schema with the
> [`linkml-author`](https://github.com/noelmcloughlin/schema-sidecar) skill
> (`npx skills add noelmcloughlin/schema-sidecar --skill linkml-author --yes`)
> and run `just --justfile .linkml/justfile lint` before committing;
> `.linkml/README.md` says what is generated and what is hand-written.
> **Agents:** read `<SCHEMA_FOLDER>/<PROJ_SLUG>.yaml` before
> the code it describes.
