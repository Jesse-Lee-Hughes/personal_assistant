import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("Missing GOOGLE_API_KEY in .env")
