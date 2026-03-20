"""
Helix Template Registry Mapping
"""
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'governance', 'templates')
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', '..')

TEMPLATE_MAP = {
    'substrate': {
        'template': os.path.join(TEMPLATE_DIR, 'substrate', 'SUBSTRATE_README_TEMPLATE.md'),
        'output_fn': lambda name: os.path.join(REPO_ROOT, 'substrates', name, 'README.md')
    },
    'pipeline': {
        'template': os.path.join(TEMPLATE_DIR, 'pipeline', 'PIPELINE_STAGE_TEMPLATE.md'),
        'output_fn': lambda name, substrate='unknown': os.path.join(REPO_ROOT, 'substrates', substrate, name, 'README.md') # Note: HIL will need to pass args or we just put it in a holding pen
    },
    'experiment': {
        'template': os.path.join(TEMPLATE_DIR, 'experiment', 'EXPERIMENT_TEMPLATE.md'),
        'output_fn': lambda name: os.path.join(REPO_ROOT, 'atlas', 'experiments', f"{name}.md")
    },
    'invariant': {
        'template': os.path.join(TEMPLATE_DIR, 'invariant', 'INVARIANT_TEMPLATE.md'),
        'output_fn': lambda name: os.path.join(REPO_ROOT, 'atlas', 'invariants', f"{name}.md")
    },
    'entity': {
        'template': os.path.join(TEMPLATE_DIR, 'entity', 'ENTITY_TEMPLATE.md'),
        'output_fn': lambda name: os.path.join(REPO_ROOT, 'atlas', 'entities', f"{name}.md")
    },
    'dataset': {
        'template': os.path.join(TEMPLATE_DIR, 'dataset', 'DATASET_TEMPLATE.md'),
        'output_fn': lambda name: os.path.join(REPO_ROOT, 'datasets', name, 'README.md')
    },
    'roadmap_entry': {
        'template': os.path.join(TEMPLATE_DIR, 'roadmap', 'ROADMAP_ENTRY_TEMPLATE.md'),
        'output_fn': lambda name: os.path.join(REPO_ROOT, 'atlas', 'roadmap', 'HELIX_ROADMAP.md'),
        'append': True
    },
    'application': {
        'template': os.path.join(TEMPLATE_DIR, 'application', 'APPLICATION_TEMPLATE.md'),
        'output_fn': lambda name: os.path.join(REPO_ROOT, 'applications', name, 'README.md')
    }
}
