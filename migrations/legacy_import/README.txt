Legacy migration scripts in /scripts import data from:
- ComputerEndProgram/STFC-Verifier
- ComputerEndProgram/STFC-Verifier-Alliance
- ComputerEndProgram/Veil-Security

Each importer should:
1) Read source database or export.
2) Map rows into shared + profile tables.
3) Record legacy source metadata for traceability.
