from jinja2 import Template
from os.path import join
import json

def get_log_dir():
    return 'logs'

def append_to_file( 
    *,
    reply: str,
    system_prompt: str,
    user_prompt: str,
    system_tokens: int,
    user_tokens: int,
    prompt_log_suffix: str = None
                   ):
    template_string = """
System: {{ system_prompt }}
System Tokens: {{ system_tokens }}
    
Human: {{ user_prompt }}
Human Tokens: {{ user_tokens }}
    
Reply: {{ reply }}
"""

    data = {
        'system_prompt': system_prompt,
        'user_prompt': user_prompt,
        'system_tokens': system_tokens,
        'user_tokens': user_tokens,
        'reply': reply
    }
    template = Template(template_string)
    rendered_template = template.render(**data)

    with open(f'{get_log_dir()}/prompts.{prompt_log_suffix}.json', 'w') as file:
        json_string = json.dumps(data)
        file.write(json_string)
    with open(f'{get_log_dir()}/prompts.{prompt_log_suffix}.txt', 'w') as file:
        file.write(rendered_template)



def append_to_prompt(
    *,
    reply: str,
    system_prompt: str,
    user_prompt: str,
    system_tokens: int,
    user_tokens: int
):
    data = {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_tokens": system_tokens,
        "user_tokens": user_tokens,
        "reply": reply
    }
    json_string = json.dumps(data)
    with open('/tmp/out.txt', 'a') as file:
        file.write(json_string + '\n')
