import re
from pathlib import Path

def strip_docstrings_and_comments(content):
    lines = content.split('\n')
    result = []
    in_docstring = False
    docstring_quote = None
    
    for line in lines:
        stripped = line.strip()
        
        if in_docstring:
            if stripped.endswith(docstring_quote):
                in_docstring = False
            continue
        
        if stripped.startswith('"""') or stripped.startswith("'''"):
            docstring_quote = '"""' if stripped.startswith('"""') else "'''"
            if not stripped.endswith(docstring_quote) or len(stripped) == 3:
                in_docstring = True
            continue
        
        if stripped.startswith('#'):
            continue
        
        result.append(line)
    
    return '\n'.join(result)

src_path = Path('src/scholaris')
count = 0

for py_file in src_path.rglob('*.py'):
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    cleaned = strip_docstrings_and_comments(content)
    
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    
    count += 1
    print(f'Processed: {py_file.relative_to("src")}')

print(f'\nTotal files processed: {count}')
