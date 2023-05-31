a vscode extension that lets the user adjust the heading level of the selected text. it should have three commands: increase heading level, decrease heading level, and set heading level
created a shared `utils.ts` file that exports the `adjustHeadingLevel` method to adjust headings
when registering commands, use an identifier that would match the following regex: "extension.(increaseHeading|decreaseHeading|setHeading)"


Important details:
- make sure the following files are present:
    - tsconfig.json
    - .gitignore
    - README.md
    - src/test/runTest.ts
- make sure the following constrants are observed in ".gitignore"
    - ignore javascript files
- make sure the following constrants are observed in "runTest.ts"
    - import "mocha" directly (eg. `import Mocha from 'mocha'`)
    - import glob as named export (eg. `import {glob} from 'glob'`)
    - do not import modules that are not needed
    - use node builtin "assert" library for assertions
    - DO NOT use parameters that have implicit 'any' type - add proper types or add an explicit 'any' type
- make sure the following shared dependencies are present
    - mocha for testing
- make sure that the README has the following sections:
    - Overview: what this project is about
    - Quickstart: how to use this extension
    - Development Guide: how to develop for this extension
- make sure the following dependencies are present in `package.json`
    - @vscode/test-electron: ^2.3.2
    - glob: ^7.1.4
    - dependencies required for testing (eg. mocha)
    - dependencies required for types (eg. @types/mocha, @types/glob)
- make sure the following dependencies are not present in `package.json`
    - "vscode-test"
- make sure the following constraints are observed in `package.json`
    - when referring to extension command, use the format "extension.{command-name}". DO NOT use the extension name as the command prefix
    - when adding "activationEvents", do not include "onCommand" directives
- make sure to include `.vscode/launch.json` as one of the mandatory files
    - it should have a "extensionHost" launch task
    - it should have "--disable-extensions" as one of the "args"
    - the "preLaunchTask" task should be "npm: compile"
- make sure that you have tests for the user specified functionality
- for all typescript code, generate correct imports according to `"esModuleInterop": true` being set in `tsconfig.json`
    - when exporting modules, ALWAYS use a named export, NEVER a default export. if the module is the only export in the file, the module name MUST BE IDENTICAL to the filename 
    - when importing modules that we have written, ALWAYS import names of modules we are using
    - when importing modules, ONLY import modules that will be used 
    - when calling a function from 'shared_dependencies', ALWAYS use the given type signature