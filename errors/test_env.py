"""
Test environment variable loading
Run: python test_env.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("="*60)
print("ENVIRONMENT VARIABLE TEST")
print("="*60)

# Get current directory
current_dir = Path.cwd()
print(f"\nCurrent directory: {current_dir}")

# Check if .env exists
env_file = current_dir / '.env'
print(f".env file exists: {env_file.exists()}")
print(f".env file path: {env_file}")

if env_file.exists():
    print(f".env file size: {env_file.stat().st_size} bytes")
    
    # Load .env
    load_dotenv(env_file, override=True)
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY', '')
    
    if api_key:
        print(f"\n✅ API Key loaded successfully!")
        print(f"   Key starts with: {api_key[:10]}...")
        print(f"   Key ends with: ...{api_key[-10:]}")
        print(f"   Key length: {len(api_key)} characters")
        
        if api_key.startswith('sk-'):
            print("   ✓ Key format looks valid")
        else:
            print("   ✗ Key format invalid (should start with 'sk-')")
    else:
        print("\n❌ API Key NOT found!")
        print("   Check your .env file format")
        
        # Show .env content (first 500 chars)
        with open(env_file, 'r') as f:
            content = f.read(500)
            print(f"\n.env file preview:\n{content[:200]}...")
else:
    print("\n❌ .env file NOT found!")
    print("   Create it in the project root directory")

print("\n" + "="*60)