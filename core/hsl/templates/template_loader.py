"""
Helix Template Loader
"""
import os

def load_template(template_path: str) -> str:
    """
    Loads a template markdown string from the governance directory.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found at: {template_path}")
        
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()
