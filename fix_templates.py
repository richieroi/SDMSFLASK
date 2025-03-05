import os
import re

def fix_template_files():
    """Fix common issues in template files"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    template_files = []
    
    # Find all template files
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                template_files.append(os.path.join(root, file))
    
    fixed_templates = []
    
    for template_file in template_files:
        # Skip base, login, and landing templates
        filename = os.path.basename(template_file)
        if filename in ['base.html', 'login.html', 'landing.html']:
            continue
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the template extends something other than base.html
        extends_match = re.search(r'{%\s*extends\s+[\'"](.+?)[\'"]\s*%}', content)
        if extends_match and extends_match.group(1) != 'base.html':
            # Fix the extends statement
            fixed_content = content.replace(extends_match.group(0), '{% extends "base.html" %}')
            
            # Write back the fixed content
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            fixed_templates.append(os.path.relpath(template_file, templates_dir))
    
    return fixed_templates

if __name__ == "__main__":
    print("Fixing template files for consistent navbar...")
    fixed = fix_template_files()
    
    if fixed:
        print("\nFixed template files:")
        for template in fixed:
            print(f"- {template}")
        print(f"\nTotal templates fixed: {len(fixed)}")
    else:
        print("All templates are already correctly extended from base.html!")
