from jinja2 import Template

def append_to_file(**kwargs):
    template_string = """
System: {{ system_prompt }}
System Tokens: {{ system_tokens }}
    
Human: {{ user_prompt }}
Human Tokens: {{ user_tokens }}
    
Reply: {{ reply }}
"""

    template = Template(template_string)
    rendered_template = template.render(**kwargs)

    with open('prompts.txt', 'a') as file:
        file.write(rendered_template)
