from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='configs/.env')

print(os.getenv('OPENAI_API_KEY'))