a vscode extension that lets the user adjust the heading level of the selected text. it should have three commands: increase heading level, decrease heading level, and set heading level

Important details:
- make sure the following files are present:
    - tsconfig.json
    - .gitignore
    - README.md
    - test/runTest.ts
    - test/suite/index.ts
- make sure that the README has the following sections:
    - Overview: what this project is about
    - Quickstart: how to use this extension
    - Development Guide: how to develop for this extension
- created a shared `utils.ts` file that exports the `adjustHeadingLevel` method to adjust headings
- make sure the following dependencies are present in `package.json`
    - @vscode/test-electron": "^2.3.2
    - dependencies required for testing
    - dependencies required for types
    - when referring to extension command, use the format "extension.{command-name}". DO NOT use the extension name as the command prefix
- make sure to include `.vscode/launch.json` as one of the mandatory files
    - it should have a "extensionHost" launch task
    - it should have "--disable-extensions" as one of the "args"
- for all typescript code, generate correct imports according to `"esModuleInterop": true` being set in `tsconfig.json`. STRONGLY prefer using a default import instead of a namespace import