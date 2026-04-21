import os
from dotenv import load_dotenv
from supabase import create_client, Client
from passlib.context import CryptContext

load_dotenv()

# Password Hashing Setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database Setup
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
sb_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL else None
