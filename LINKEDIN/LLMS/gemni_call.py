import textwrap
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os

## print the key
print(os.getenv('GENAI_API_KEY'))

class GeminiLLM:
    def __init__(self, api_key_env_var='GENAI_API_KEY',model = "pro"):
        load_dotenv()  # Load environment variables from .env file
        self.api_key = os.getenv(api_key_env_var)
        self.model = model
        if not self.api_key:
            raise ValueError(f"API key not found in environment variable '{api_key_env_var}'")
        self.model = self.configure_genai(self.api_key,self.model)

    def configure_genai(self, api_key,model):
        genai.configure(api_key=api_key)
        if self.model == "pro":
            return genai.GenerativeModel('gemini-pro')
        elif self.model == "flash":
            return genai.GenerativeModel('gemini-1.5-flash')
        else:
            return genai.GenerativeModel('gemini-pro')

    def run(self, prompt):
        response = self.model.generate_content(prompt)
        markdown = self.to_markdown(response.text)
        return markdown
      
    def to_markdown(self, text):
        text = text.replace('•', '  *')
        return textwrap.indent(text, '')

# Usage example
# content_generator = GeminiLLM()
# prompt = "Write a short story about a robot learning to play chess.Satirical and short.Response in markdown only."
# generated_content = content_generator.run(prompt)
# print(generated_content)