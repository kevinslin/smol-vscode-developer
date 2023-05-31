# smol-vscode-developer

This is a fork of [smol-developer](https://github.com/smol-ai/developer?ref=producthunt). For the original README, please check out the link.

This readme goes over changes from the original

## quickstart

```sh
pipenv shell
pipenv install
# Generate a vscode extension that increases/decreases headers
python main_no_modal.py prompts/prompt-vscode.md 
```

## options

###  --start-from <step>
- values:
  - 1_generate_file_list: generate files used for code generation
  - 2_generate_shared_libraries: generated shared dependencies
  - 3_generate_code: generated code only
    - > NOTE: this requires that you pass in a list of comma delimited files to regenerate

allows you to specify where to begin generation. if specified, will ONLY execute the specific step

## examples

### regenerate specific files
```sh
python main_no_modal.py prompts/prompt-vscode.md generated src/extension.ts,src/commands/decreaseHeading.ts,src/commands/setHeading.ts,src/commands/increaseHeading.ts --start-from 3_generate_code
```