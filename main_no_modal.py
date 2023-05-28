import ast
import json
import os
import sys
from time import sleep
from enum import Enum
from typing import Optional

from developer.utils import append_to_file, get_log_dir

generatedDir = "generated"
openai_model = "gpt-4"  # or 'gpt-3.5-turbo',
openai_model_max_tokens = 2000  # i wonder how to tweak this properly


class Checkpoint(Enum):
    GENERATE_FILE_LIST = "1_generate_file_list"
    GENERATE_SHARED_LIBRARIES = "2_generate_shared_libraries"
    GENERATE_CODE = "3_generate_code"

def generate_response(system_prompt, user_prompt, *args, prompt_log_suffix: Checkpoint=None):
    import openai
    import tiktoken

    def reportTokens(prompt):
        encoding = tiktoken.encoding_for_model(openai_model)
        # print number of tokens in light gray, with first 10 characters of prompt in green
        print(
            "\033[37m"
            + str(len(encoding.encode(prompt)))
            + " tokens\033[0m"
            + " in prompt: "
            + "\033[92m"
            + prompt[:50]
            + "\033[0m"
        )
        return len(encoding.encode(prompt))

    # Set up your OpenAI API credentials
    openai.api_key = os.environ["OPENAI_API_KEY"]

    messages = []
    messages.append({"role": "system", "content": system_prompt})
    system_tokens = reportTokens(system_prompt)
    messages.append({"role": "user", "content": user_prompt})
    user_tokens = reportTokens(user_prompt)
    # loop thru each arg and add it to messages alternating role between "assistant" and "user"
    role = "assistant"
    for value in args:
        messages.append({"role": role, "content": value})
        reportTokens(value)
        role = "user" if role == "assistant" else "assistant"

    params = {
        "model": openai_model,
        "messages": messages,
        "max_tokens": openai_model_max_tokens,
        "temperature": 0,
    }

    # Send the API request
    keep_trying = True
    while keep_trying:
        try:
            response = openai.ChatCompletion.create(**params)
            keep_trying = False
        except Exception as e:
            # e.g. when the API is too busy, we don't want to fail everything
            print("Failed to generate response. Error: ", e)
            sleep(30)
            print("Retrying...")

    # Get the reply from the API response
    reply = response.choices[0]["message"]["content"]
    append_to_file(system_prompt=system_prompt, user_prompt=user_prompt, system_tokens=system_tokens, 
                   user_tokens=user_tokens, reply=reply, prompt_log_suffix=prompt_log_suffix)
    return reply


def generate_file(
    filename, filepaths_string=None, shared_dependencies=None, prompt=None
):
    # call openai api with this prompt
    filecode = generate_response(
        f"""You are an AI developer who is trying to write a program that will generate code for the user based on their intent.

    the app is: {prompt}

    the files we have decided to generate are: {filepaths_string}

    the shared dependencies (like filenames and variable names) we have decided on are: {shared_dependencies}

    only write valid code for the given filepath and file type, and return only the code.
    do not add any other explanation, only return valid code for that file type.
    """,
        f"""
    We have broken up the program into per-file generation.
    Now your job is to generate only the code for the file {filename}.
    Make sure to have consistent filenames if you reference other files we are also generating.

    Remember that you must obey 3 things:
       - you are generating code for the file {filename}
       - do not stray from the names of the files and the shared dependencies we have decided on
       - MOST IMPORTANT OF ALL - the purpose of our app is {prompt} - every line of code you generate must be valid code. Do not include code fences in your response, for example

    Bad response:
    ```javascript
    console.log("hello world")
    ```

    Good response:
    console.log("hello world")

    Begin generating the code now.

    """,
    )

    return filename, filecode


def should_generate_file_list(start_from: Optional[Checkpoint] = None):
    if start_from is None:
        return True 
    return False

def should_generate_shared_deps(start_from: Optional[Checkpoint] = None):
    if start_from == Checkpoint.GENERATE_CODE.value:
        return False
    return True

def should_clean_dir(start_from: Optional[Checkpoint] = None):
    if start_from is None:
        return True
    if start_from == Checkpoint.GENERATE_CODE.value:
        return False

def read_file_list_from_disk():
    log_dir = get_log_dir()
    with open(os.path.join(log_dir, 'prompts.0.json'), 'r') as file:
        file_list = json.load(file)['reply']
        return file_list

def main(prompt, directory=generatedDir, file=None,  start_from = None):
    # read file from prompt if it ends in a .md filetype
    if prompt.endswith(".md"):
        with open(prompt, "r") as promptfile:
            prompt = promptfile.read()

    print("hi its me, 🐣the smol developer🐣! you said you wanted:")
    # print the prompt in green color
    print("\033[92m" + prompt + "\033[0m")


    if should_generate_file_list(start_from):
        # call openai api with this prompt
        filepaths_string = generate_response(
            """You are an AI developer who is trying to write a program that will generate code for the user based on their intent.

        When given their intent, create a complete, exhaustive list of filepaths that the user would write to make the program.

        only list the filepaths you would write, and return them as a python list of strings.
        do not add any other explanation, only return a python list of strings.
        """,
            prompt,
            prompt_log_suffix=Checkpoint.GENERATE_FILE_LIST
        )
    else:
        print("reading file list from disk")
        filepaths_string = read_file_list_from_disk()
    sys.exit()
    # parse the result into a python list
    list_actual = []
    try:
        list_actual = ast.literal_eval(filepaths_string)
        print(list_actual)

        # if shared_dependencies.md is there, read it in, else set it to None
        shared_dependencies = None
        if os.path.exists("shared_dependencies.md"):
            with open("shared_dependencies.md", "r") as shared_dependencies_file:
                shared_dependencies = shared_dependencies_file.read()

        if file is not None:
            # check file
            print("file", file)
            filename, filecode = generate_file(
                file,
                filepaths_string=filepaths_string,
                shared_dependencies=shared_dependencies,
                prompt=prompt,
            )
            write_file(filename, filecode, directory)
        else:
            if should_clean_dir(start_from):
                print("cleaning directory ", directory)
                clean_dir(directory)

            if should_generate_shared_deps(start_from):
                # understand shared dependencies
                shared_dependencies = generate_response(
                    """You are an AI developer who is trying to write a program that will generate code for the user based on their intent.

                In response to the user's prompt:

                ---
                the app is: {prompt}
                ---

                the files we have decided to generate are: {filepaths_string}

                Now that we have a list of files, we need to understand what dependencies they share.
                Please name and briefly describe what is shared between the files we are generating, including exported variables, data schemas, id names of every DOM elements that javascript functions will use, message names, and function names.
                Exclusively focus on the names of the shared dependencies, and do not add any other explanation.
                """,
                    prompt,
                    prompt_log_suffix=Checkpoint.GENERATE_SHARED_LIBRARIES
                )
                print(shared_dependencies)
                # write shared dependencies as a md file inside the generated directory
                write_file("shared_dependencies.md", shared_dependencies, directory)
            else:
                with open(os.path.join(directory, 'shared_dependencies.md'), 'r') as file:
                    shared_dependencies = file.read()

            print("generating files: ", list_actual, "in directory", directory, "with shared dependencies", shared_dependencies)
            for name in list_actual:
                filename, filecode = generate_file(
                    name,
                    filepaths_string=filepaths_string,
                    shared_dependencies=shared_dependencies,
                    prompt=prompt,
                )
                write_file(filename, filecode, directory)

    except ValueError:
        print("Failed to parse result: " + result)


def write_file(filename, filecode, directory):
    # Output the filename in blue color
    print("\033[94m" + filename + "\033[0m")
    print(filecode)

    file_path = directory + "/" + filename
    dir = os.path.dirname(file_path)
    os.makedirs(dir, exist_ok=True)

    # Open the file in write mode
    with open(file_path, "w") as file:
        # Write content to the file
        file.write(filecode)


def clean_dir(directory):
    extensions_to_skip = [
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".svg",
        ".ico",
        ".tif",
        ".tiff",
    ]  # Add more extensions if needed

    # Check if the directory exists
    if os.path.exists(directory):
        # If it does, iterate over all files and directories
        for root, dirs, files in os.walk(directory):
            for file in files:
                _, extension = os.path.splitext(file)
                if extension not in extensions_to_skip:
                    os.remove(os.path.join(root, file))
    else:
        os.makedirs(directory, exist_ok=True)


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="Prompt to provide")
    parser.add_argument("directory", nargs="?", default="generated", help="Directory path")
    parser.add_argument("file", nargs="?", help="File name")
    parser.add_argument(
        "-s",
        "--start-from",
        choices=["1_generate_file_list", "2_generate_shared_libraries", "3_generate_code"],
        help="Specify the starting point",
    )
    args = parser.parse_args()

    prompt = args.prompt
    directory = args.directory
    file = args.file
    start_from = args.start_from
    main(prompt, directory, file, start_from)
