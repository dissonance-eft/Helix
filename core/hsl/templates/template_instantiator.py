"""
Helix Template Instantiator
"""
import os
from datetime import datetime
from .template_registry import TEMPLATE_MAP
from .template_loader import load_template

def instantiate_template(type_name: str, instance_name: str, author: str = "Operator") -> str:
    """
    Instantiates a governance template and writes it to the repository.
    Returns the path where the file was written.
    """
    if type_name not in TEMPLATE_MAP:
        raise ValueError(f"Unknown template type: {type_name}")
        
    config = TEMPLATE_MAP[type_name]
    template_path = config['template']
    output_path = config['output_fn'](instance_name)
    is_append = config.get('append', False)
    
    # Load
    raw_content = load_template(template_path)
    
    # Replace placeholders
    date_str = datetime.now().strftime("%Y-%m-%d")
    content = raw_content.replace("{name}", instance_name)
    content = content.replace("{date}", date_str)
    content = content.replace("{author}", author)
    content = content.replace("{operator}", author)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write or Append
    if is_append:
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write("\n\n" + content + "\n")
    else:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    return output_path
