import os
import json
import uuid
import openai
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

openai.organization = "org-FiDs6DCZYfx0I1xd8jTzGH8Q"
openai.api_key = os.getenv("OPENAI_API_KEY")
resp = openai.Model.list()

def parse_response(text, parse_code=True):
    code_position = text.find('```')
    if code_position >= 0 and parse_code:
        results = text.split('```', maxsplit=2)
        if len(results) == 2:
            pre, codes = results
            remaining = ''
        else:
            pre, codes, remaining = results
        #codes = codes.split(maxsplit=1)[1]
        formatter = HtmlFormatter(style='colorful')
        codes = '<code class="hljs language-python">%s</code>' % highlight(codes, PythonLexer(), formatter)
        remaining = parse_response(remaining) if remaining else ''
    else:
        pre, codes, remaining = text, '', ''
    paragraphs = pre.strip('\n').split('\n')
    paragraphs = ['<p>%s</p>' % (p, ) for p in paragraphs]
    outputs = ''.join(paragraphs) + codes + remaining
    return outputs


class Chat:
    def __init__(self, chat_id=None, system_prompts='', model='gpt-3.5-turbo-0301', history=[], logdir='log'):
        os.makedirs(logdir, exist_ok=True)
        self.chat_id = chat_id or str(uuid.uuid4())
        self.model = model
        self.messages = [{'role': 'system', 'content': system_prompts}, *history]
    
    def say(self, content, html_code_prettify=True):
        self.append_history('user', content)
        completion = openai.ChatCompletion.create(model=self.model, messages=self.messages)
        response_message = str(completion['choices'][0]['message']['content']).strip()
        self.append_history('assistant', str(response_message))
        self.dump_history()
        return parse_response(response_message, parse_code=html_code_prettify)
        
    def append_history(self, role, content):
        self.messages.append({'role': role, 'content': content})

    def dump_history(self, ):
        with open('log/%s.txt' % (self.chat_id, ), 'w') as f:
            json.dump(json.dumps(self.messages, ), f)


        
