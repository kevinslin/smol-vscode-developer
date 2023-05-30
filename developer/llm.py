import os
from time import sleep

import aiofiles
import openai

from developer.schema import Checkpoint
from developer.utils import append_to_file, to_kebab_case

generatedDir = "generated"
openai_model = "gpt-4"  # or 'gpt-3.5-turbo',
openai_model_max_tokens = 2000  # i wonder how to tweak this properly

def generate_response(system_prompt, user_prompt, *args, prompt_log_suffix:str=""):
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
    reply = None
    while keep_trying:
        try:
            response = openai.ChatCompletion.create(**params) # type: ignore
            keep_trying = False
            reply = response.choices[0]["message"]["content"]
        except Exception as e:
            # e.g. when the API is too busy, we don't want to fail everything
            print("Failed to generate response. Error: ", e)
            sleep(30)
            print("Retrying...")

    if not reply:
        raise Exception("OpenAI returned an empty response")

    append_to_file(system_prompt=system_prompt, user_prompt=user_prompt, system_tokens=system_tokens, 
                   user_tokens=user_tokens, reply=reply, prompt_log_suffix=prompt_log_suffix)
    return reply

async def generate_file(
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
- when using functions from the shared dependencies, use the function signatures we have decided on. DO NOT call functions with arguments that do not match THE FUNCTION SIGNATURES 
- MOST IMPORTANT OF ALL - the purpose of our app is {prompt} - every line of code you generate must be valid code. Do not include code fences in your response, for example

Bad response:
```javascript
console.log("hello world")
```

Good response:
console.log("hello world")

Begin generating the code now.
    """,
    prompt_log_suffix=Checkpoint.GENERATE_CODE.value + "-" + to_kebab_case(filename)
    )

    return filename, filecode

async def generate_and_write_code_file(name, filepaths_string, shared_dependencies, prompt, directory):
    filename, filecode = await generate_file(
        name,
        filepaths_string=filepaths_string,
        shared_dependencies=shared_dependencies,
        prompt=prompt,
    )

    fpath = f"{directory}/{filename}"
    # make sure directory exists
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    async with aiofiles.open(f'{directory}/{filename}', 'w') as f:
        await f.write(filecode)
