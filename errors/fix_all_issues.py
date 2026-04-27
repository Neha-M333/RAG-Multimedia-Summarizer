"""
Fix all issues at once
Run: python fix_all_issues.py
"""
import os
from pathlib import Path

def fix_streamlit_warnings():
    """Fix Streamlit deprecation warnings"""
    print("📝 Fixing Streamlit warnings...")
    
    files = ['app.py', 'pages/1_Upload.py', 'pages/2_Chat.py', 'pages/3_History.py']
    
    for filepath in files:
        if not Path(filepath).exists():
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace('use_container_width=True', "width='stretch'")
        content = content.replace('use_container_width=False', "width='content'")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✓ Fixed {filepath}")

def check_ollama():
    """Check if Ollama is running"""
    print("\n🔍 Checking Ollama status...")
    
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("  ✓ Ollama is running")
            
            # Check installed models
            models = response.json().get('models', [])
            if models:
                print(f"  ✓ Found {len(models)} model(s):")
                for model in models:
                    print(f"    - {model['name']}")
            else:
                print("  ⚠ No models installed. Run: ollama pull llama3.2")
            return True
        else:
            print("  ❌ Ollama is not responding correctly")
            return False
    except Exception as e:
        print(f"  ❌ Ollama is not running or not accessible")
        print(f"     Error: {e}")
        print("\n  To fix:")
        print("    1. Install Ollama: https://ollama.com/download")
        print("    2. Run: ollama serve")
        print("    3. Download model: ollama pull llama3.2")
        return False

def verify_local_llm():
    """Verify local_llm.py has all required methods"""
    print("\n🔍 Verifying LocalRAGEngine...")
    
    filepath = 'backend/local_llm.py'
    
    if not Path(filepath).exists():
        print(f"  ❌ {filepath} not found!")
        print("     Please create it with the code provided above")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_methods = [
        'chunk_text',
        'generate_answer',
        'summarize_text',
        'extract_keywords',
        'generate_questions',
        'chat_with_context'
    ]
    
    missing = []
    for method in required_methods:
        if f'def {method}' not in content:
            missing.append(method)
    
    if missing:
        print(f"  ❌ Missing methods: {', '.join(missing)}")
        print("     Please update local_llm.py with the complete code above")
        return False
    else:
        print("  ✓ LocalRAGEngine has all required methods")
        return True

def check_env_config():
    """Check .env configuration"""
    print("\n🔍 Checking .env configuration...")
    
    if not Path('.env').exists():
        print("  ⚠ .env file not found")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'USE_LOCAL_LLM=true' in content:
        print("  ✓ USE_LOCAL_LLM is enabled")
        return True
    else:
        print("  ⚠ USE_LOCAL_LLM not set to true")
        print("     Add this to .env:")
        print("     USE_LOCAL_LLM=true")
        print("     OLLAMA_MODEL=llama3.2")
        return False

def main():
    print("="*60)
    print("🔧 AI Summarization System - Complete Fix")
    print("="*60)
    
    # Fix 1: Streamlit warnings
    fix_streamlit_warnings()
    
    # Fix 2: Check Ollama
    ollama_ok = check_ollama()
    
    # Fix 3: Verify local_llm.py
    llm_ok = verify_local_llm()
    
    # Fix 4: Check .env
    env_ok = check_env_config()
    
    print("\n" + "="*60)
    print("📊 Status Summary")
    print("="*60)
    print(f"Streamlit warnings: ✓ Fixed")
    print(f"Ollama service:     {'✓ Running' if ollama_ok else '❌ Not running'}")
    print(f"LocalRAGEngine:     {'✓ Complete' if llm_ok else '❌ Incomplete'}")
    print(f".env config:        {'✓ Correct' if env_ok else '⚠ Needs update'}")
    print("="*60)
    
    if ollama_ok and llm_ok and env_ok:
        print("\n✅ All issues fixed! Ready to run.")
        print("\n🚀 Start with: streamlit run app.py")
    else:
        print("\n⚠ Some issues remain. Please fix them before running.")
        
        if not ollama_ok:
            print("\n📌 Next step: Start Ollama")
            print("   Run: ollama serve")
            print("   Then: ollama pull llama3.2")
        
        if not llm_ok:
            print("\n📌 Next step: Update backend/local_llm.py")
            print("   Copy the complete code from the fix above")
        
        if not env_ok:
            print("\n📌 Next step: Update .env file")
            print("   Add: USE_LOCAL_LLM=true")

if __name__ == "__main__":
    main()