import os
import json
from dotenv import load_dotenv
from groq import Groq

class GroqLLM:
    def __init__(self, api_key_env_var='GROQ_API_KEY'):
        """
        Initializes the ContentGenerator with the Groq API client.

        Args:
        - api_key_env_var (str): Environment variable name where the Groq API key is stored.
        """
        load_dotenv()  # Load environment variables from .env file
        api_key = os.getenv(api_key_env_var)
        if not api_key:
            raise ValueError(f"{api_key_env_var} not found in environment variables.")
        
        self.client = Groq(api_key=api_key)

    def run(self, prompt):
        """
        Generates content based on a dynamic prompt using the Groq API.

        Args:
        - prompt (str): The prompt to generate content for.
        
        Returns:
        - str: The generated content.
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                # model="mixtral-8x7b-32768",
                model="deepseek-r1-distill-llama-70b",
            )
            return chat_completion.choices[0].message.content.split("</think>")[1].strip()
        except Exception as e:
            print(f"Error generating content: {e}")
            return ""

# # Usage example
# # Ensure you have a .env file in your project root with GROQ_API_KEY set
# content_generator = GroqLLM()
# generated_content = content_generator.run("Tell me a joke about computers.")
# print(generated_content)
