"""
Fix Streamlit deprecation warnings
Run: python fix_streamlit.py
"""
import os
from pathlib import Path

def fix_file(filepath):
    """Fix use_container_width in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count occurrences
        count = content.count('use_container_width')
        
        if count > 0:
            # Replace use_container_width=True with width='stretch'
            content = content.replace('use_container_width=True', "width='stretch'")
            
            # Replace use_container_width=False with width='content'
            content = content.replace('use_container_width=False', "width='content'")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Fixed {count} occurrence(s) in: {filepath}")
            return True
        else:
            print(f"  No issues in: {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    print("="*60)
    print("Fixing Streamlit Deprecation Warnings")
    print("="*60)
    print()
    
    files_to_check = [
        'app.py',
        'pages/1_Upload.py',
        'pages/2_Chat.py',
        'pages/3_History.py'
    ]
    
    fixed_count = 0
    
    for filepath in files_to_check:
        if Path(filepath).exists():
            if fix_file(filepath):
                fixed_count += 1
        else:
            print(f"⚠ File not found: {filepath}")
    
    print()
    print("="*60)
    print(f"✅ Fixed {fixed_count} file(s)")
    print("="*60)
    print()
    print("Next: Restart Streamlit with: streamlit run app.py")

if __name__ == "__main__":
    main()