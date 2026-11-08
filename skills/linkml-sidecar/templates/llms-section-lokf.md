## Schema

The data model of this repository is a LinkML schema at
`<SCHEMA_FOLDER>/<PROJ_SLUG>.yaml`, also reachable as
`linkml_schema/`. Read it before the code it describes. Every class, field
and enum is defined once there, with its meaning mapped to public
vocabularies. The JSON Schema, OWL and the rest under `.linkml/project/`
and the Pydantic models under `.linkml/src/<PROJ_SLUG>/datamodel/` are
generated from it, never edited. Change the schema
through the `linkml-author` skill (`npx skills add
noelmcloughlin/linkml-sidecar --skill linkml-author --yes`), and run
`just --justfile .linkml/justfile lint` and `test` before committing.

The `.lokf/` knowledge bundle validates its concepts against a copy of
this schema, `.lokf/schema/<PROJ_SLUG>.yaml`, which `lokf adapt` writes
(`just --justfile .linkml/justfile lokf-adapt`). Edit the schema, never the
copy: a concept whose `type` names one of its classes carries only the
fields that class declares.
