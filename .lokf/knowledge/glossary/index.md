# Glossary

* [Sidecar](sidecar.md) - A hidden folder, .linkml/, that holds a complete schema project beside a host's own code, around a dummy schema or a schema the host already holds, with nothing in the host's build depending on it.
* [Doorway](doorway.md) - The linkml_schema link at the host's root that shows the hidden sidecar's schema folder under an ordinary, visible name.
* [Dummy schema](dummy-schema.md) - The small placeholder schema a fresh sidecar holds, a Person example in both plain and KTL mode, which lints clean and which linkml-author replaces with the host's real model.
* [Template pin](template-pin.md) - The one place the linkml-project-copier version is fixed: LINKML_TEMPLATE_REF and LINKML_TEMPLATE_SHA in the scaffold driver, a tag verified against its commit before copier runs with --trust.
* [Domain schema](domain-schema.md) - A LinkML schema that models a domain and that a LinkML project owns, in .linkml/src/<slug>/schema/ or src/<slug>/schema/; it imports nothing from .lokf/, and the skills take it as far as a published release, which a KTL bundle may adapt into its domain vocabulary.
* [The gate](the-gate.md) - linkml-author's check after every schema edit: lint, then gen-project, then test, through the project's justfile or Makefile, or the three LinkML tools directly for a schema with no project, with lokf adapt and lokf validate after it beside a KTL bundle with a copy of the schema.
* [Domain vocabulary](domain-vocabulary.md) - The schema files a KTL bundle keeps in .lokf/schema/: published, curated vocabulary that ktl-librarian builds with lokf adapt from published schemas of this repository or any other, or from none; the bundle's own, which neither skill writes.
