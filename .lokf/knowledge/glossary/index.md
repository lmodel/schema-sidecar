# Glossary

* [Sidecar](sidecar.md) - A hidden folder, .linkml/, that holds a complete schema project beside a host's own code, around a dummy schema or a schema the host already holds, with nothing in the host's build depending on it.
* [Doorway](doorway.md) - The linkml_schema link at the host's root that shows the hidden sidecar's schema folder under an ordinary, visible name.
* [Dummy schema](dummy-schema.md) - The small placeholder schema a fresh sidecar holds, a Person example in both plain and KTL mode, which lints clean and which linkml-author replaces with the host's real model.
* [Template pin](template-pin.md) - The one place the linkml-project-copier version is fixed: LINKML_TEMPLATE_REF and LINKML_TEMPLATE_SHA in the scaffold driver, a tag verified against its commit before copier runs with --trust.
* [Domain schema](domain-schema.md) - A LinkML schema that models a domain, owned by a LinkML project in .linkml/src/<slug>/schema/ or src/<slug>/schema/; it never imports lokf, and a bundle uses its classes through the copy lokf adapt writes into .lokf/schema/, the bundle's domain vocabulary.
* [The gate](the-gate.md) - linkml-author's check after every schema edit: lint, then gen-project, then test, through the project's justfile or Makefile, or the three LinkML tools directly for a schema with no project, with lokf validate after it beside a KTL bundle that names the schema.
* [Domain vocabulary](domain-vocabulary.md) - The bundle's file in .lokf/schema/ that .lokf/justfile names on its schema := line, with every file it imports; it always imports lokf, lists the classes a concept may name beyond LOKF's own, and lokf validate --schema checks the bundle against it; in KTL mode it is the copy lokf adapt writes from the sidecar's schema.
