import os
from dotenv import load_dotenv

# Get absolute path of .env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Load .env explicitly
load_dotenv(dotenv_path=ENV_PATH, override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("LOADED KEY:", GROQ_API_KEY)