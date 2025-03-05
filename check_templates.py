import os
import re

def check_templates_for_base_extension():
    """Check all templates to ensure they extend the base template correctly"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    template_files = []
    
    # Recursively find all template files
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                template_files.append(os.path.join(root, file))
    
    issues_found = []
    for template_file in template_files:
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Skip base template itself
            if os.path.basename(template_file) == 'base.html':
                continue
                
            # Skip partial templates (fragments that might not extend base)
            if os.path.basename(template_file).startswith('_'):
                continue
            
            # Check for extends statement
            extends_match = re.search(r'{%\s*extends\s+[\'"](.+?)[\'"]\s*%}', content)
            
            if not extends_match:
                relative_path = os.path.relpath(template_file, templates_dir)
                issues_found.append(f"MISSING EXTENDS: {relative_path}")
            elif extends_match.group(1) != 'base.html':
                relative_path = os.path.relpath(template_file, templates_dir)
                issues_found.append(f"WRONG BASE: {relative_path} extends '{extends_match.group(1)}' instead of 'base.html'")
    
    return issues_found

if __name__ == '__main__':
    print("Checking templates for proper base.html extension...")
    issues = check_templates_for_base_extension()
    
    if issues:
        print("\nIssues found in templates:")
        for issue in issues:
            print(f"- {issue}")
        print(f"\nTotal issues: {len(issues)}")
    else:
        print("All templates are correctly extending base.html!")
