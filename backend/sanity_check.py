print("Hello World - Python is running")
import os
print("Imported os")
import sys
print("Imported sys")
try:
    from dotenv import load_dotenv
    print("Imported dotenv")
except ImportError:
    print("Failed to import dotenv")

try:
    from supabase import create_client
    print("Imported supabase")
except ImportError:
    print("Failed to import supabase")
