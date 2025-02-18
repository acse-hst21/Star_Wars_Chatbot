import os

# Database configuration with default values
POSTGRES_USER = os.getenv("POSTGRES_USER", "username")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

STAR_WARS_CHARACTERS = ['C-3PO',
                        'Yoda', 
                        'Luke Skywalker', 
                        'Jar Jar Binks', 
                        'Emperor Palpatine']

def prompt_text(text):
    return f'Answer the question in the style of {text} from Star Wars'

DEFAULT_PROMPTS = [{'prompt': prompt_text(character), 
                    'name': character, 
                    'weight': 0.2} for character in STAR_WARS_CHARACTERS]

# OpenAI configuration
OPENAI_MODEL = "gpt-3.5-turbo"