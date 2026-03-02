import os
from pathlib import Path

ROOT = Path('c:/Users/dissonance/Desktop/Helix')

substitutions = [
    ('from infra.os', 'from runtime.os'),
    ('import infra.os', 'import runtime.os'),
    ('from infra', 'from runtime.infra'),
    ('import infra', 'import runtime.infra'),
    ('from layers', 'from sandbox.layers'),
    ('import layers', 'import sandbox.layers'),
    ('from data', 'from sandbox.data'),
    ('import data', 'import sandbox.data'),
]

def refactor_file(file_path):
    print(f"Refactoring {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for old, new in substitutions:
        new_content = new_content.replace(old, new)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file_path}")

for py_file in ROOT.glob('**/*.py'):
    # Skip temporary files
    if 'tmp' in str(py_file) or '.git' in str(py_file):
        continue
    refactor_file(py_file)
