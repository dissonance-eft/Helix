from __future__ import annotations
import os
from pathlib import Path
from atlas_interface.atlas_indexer import AtlasIndexer
from atlas_interface.page_builder import PageBuilder

class WikiExporter:
    """
    Exports the Helix Atlas as a static wiki in Markdown/MediaWiki format.
    """
    def __init__(self, output_dir: str = "helix_wiki"):
        self.output_dir = Path(output_dir)
        self.indexer = AtlasIndexer()

    def export(self):
        print(f"[wiki_exporter] Exporting Atlas to {self.output_dir}...")
        index = self.indexer.build_index()
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "experiments").mkdir(exist_ok=True)
        (self.output_dir / "invariants").mkdir(exist_ok=True)
        
        # 1. Main Page
        self._write_file("Main_Page.md", self._build_main_page(index))
        
        # 2. Experiment Pages
        for exp in index["experiments"]:
            # In a real system we would load the actual artifact JSON
            # Here we generate a stub
            page = PageBuilder.build_experiment_page(exp["id"], {})
            self._write_file(f"experiments/{exp['id']}.md", page)
            
        # 3. Invariant Pages
        for inv in index["invariants"]:
            page = PageBuilder.build_invariant_page(inv["name"], inv["data"])
            self._write_file(f"invariants/{inv['name']}.md", page)
            
        print("[wiki_exporter] Wiki export complete.")

    def _build_main_page(self, index: dict) -> str:
        lines = [
            "# Helix Atlas Knowledge Wiki",
            "Welcome to the automated discovery archive of the Helix system.",
            "",
            "## Exploration",
            f"* [[invariants/index|All Invariants]] ({len(index['invariants'])})",
            f"* [[experiments/index|Experiment Logs]] ({len(index['experiments'])})",
            "",
            "## Domains",
        ]
        for domain in index["domains"]:
            lines.append(f"* {domain.title()}")
        return "\n".join(lines)

    def _write_file(self, filename: str, content: str):
        path = self.output_dir / filename
        with open(path, "w") as f:
            f.write(content)
