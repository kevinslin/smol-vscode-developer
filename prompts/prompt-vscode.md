a vscode extension that lets the user adjust the heading level of the selected text. it should have three commands: increase heading level, decrease heading level, and set heading level

Important details:
- make sure the following files are present:
    - tsconfig.json
    - .gitignore
    - README.md
    - test/runTest.ts
- make sure that the README has the following sections:
    - Overview: what this project is about
    - Quickstart: how to use this extension
    - Development Guide: how to develop for this extension
- make sure the following dependencies are present in `package.json`
    - @vscode/test-electron": "^2.3.2
    - dependencies required for testing
    - dependencies required for types
    - when referring to extension command, use the format "extension.{command-name}". DO NOT use the extension name as the command prefix
    - when adding "activationEvents", do not include "onCommand" directives
- make sure to include `.vscode/launch.json` as one of the mandatory files
    - it should have a "extensionHost" launch task
    - it should have "--disable-extensions" as one of the "args"
    - the "preLaunchTask" task should be "npm: compile"
- for all typescript code, generate correct imports according to `"esModuleInterop": true` being set in `tsconfig.json`
    - when exporting modules, ALWAYS use a named export, NEVER a default export. if the module is the only export in the file, the module name should be identical to the filename
    - when importing modules that we have written, ALWAYS import names of modules we are using
    - when importing modules, ONLY import modules that will be used 
- created a shared `utils.ts` file that exports the `adjustHeadingLevel` method to adjust headings