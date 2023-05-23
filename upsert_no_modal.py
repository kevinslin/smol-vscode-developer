import sys
import os
import ast
from time import sleep
import openai
import tiktoken
import re

generatedDir = "generated"
openai_model = "gpt-4"  # or 'gpt-3.5-turbo',
openai_model_max_tokens = 2000  # i wonder how to tweak this properly

def generate_response(system_prompt, user_prompt, *args):
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

    # Set up your OpenAI API credentials
    openai.api_key = os.environ["OPENAI_API_KEY"]

    messages = []
    messages.append({"role": "system", "content": system_prompt})
    reportTokens(system_prompt)
    messages.append({"role": "user", "content": user_prompt})
    reportTokens(user_prompt)
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
    return reply

def generate_file(
    filename, file_prompt, filepaths_string=None, shared_dependencies=None, prompt=None
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
    {filename} does the following: {file_prompt}
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

def main(app_prompt, file, file_prompt, directory=generatedDir, ):
    # read file from prompt if it ends in a .md filetype
    if app_prompt.endswith(".md"):
        with open(app_prompt, "r") as promptfile:
            app_prompt = promptfile.read()
    file_list = ["tsconfig.json", "package.json", "utils.ts", "extension.ts"] + [file]
    try:
      shared_dependencies_path = os.path.join(directory, "shared_dependencies.md")
      print("shared_dependencies_path", shared_dependencies_path)
      with open(shared_dependencies_path, "r") as shared_dependencies_file:
          prefix = "the files we have decided to generate are:"
          shared_dependencies = shared_dependencies_file.read()
          # regex replace everything following the literal string "the files we have decided to generate are: " with the string "foo.md"
          shared_dependencies = re.sub(
              prefix + ".*",
              prefix + f' {", ".join(file_list)}',
              shared_dependencies,
          )
          print("file list: ", file_list)
          filename, filecode = generate_file(
              file,
              filepaths_string=", ".join(file_list),
              file_prompt=file_prompt,
              shared_dependencies=shared_dependencies,
              prompt=app_prompt,
          )
          write_file("shared_dependencies.md", shared_dependencies, directory)
          write_file(filename, filecode, directory)
      pass
    except Exception as e:
        print("Failed")
        print(e)



main(app_prompt="prompt-vscode.md", file="launch.json", file_prompt="launches the vscode extension in development mode in vscode", directory="generated")