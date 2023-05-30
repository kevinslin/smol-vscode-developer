from jinja2 import Template
import json
import os
import aiofiles

def get_log_dir():
    return 'logs'

def get_current_time_epoch():
    import time
    current_time_epoch = int(time.time())
    return current_time_epoch

def to_kebab_case(string):
    # Replace spaces and underscores with hyphens
    string = string.replace(' ', '-').replace('_', '-').replace('/', '-')
    # Convert to lowercase
    string = string.lower()
    
    return string


def append_to_file( 
    *,
    reply: str,
    system_prompt: str,
    user_prompt: str,
    system_tokens: int,
    user_tokens: int,
    prompt_log_suffix: str = "" 
                   ):
    template_string = """
System: {{ system_prompt }}
System Tokens: {{ system_tokens }}
    
Human: {{ user_prompt }}
Human Tokens: {{ user_tokens }}
    
Reply: 
{{ reply }}
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

    with open(f'{get_log_dir()}/prompts.{prompt_log_suffix}.{get_current_time_epoch()}.json', 'w') as file:
        json_string = json.dumps(data)
        file.write(json_string)
    with open(f'{get_log_dir()}/prompts.{prompt_log_suffix}.{get_current_time_epoch()}.txt', 'w') as file:
        file.write(rendered_template)


