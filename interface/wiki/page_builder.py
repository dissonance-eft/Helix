from __future__ import annotations
from atlas_interface.template_engine import TemplateEngine

class PageBuilder:
    """
    Constructs Wikipedia-style pages for Atlas objects.
    """
    
    @staticmethod
    def build_experiment_page(exp_id: str, data: dict) -> str:
        infobox = TemplateEngine.render_infobox("Experiment", [
            ("ID", exp_id),
            ("Engine", data.get("engine", "unknown")),
            ("Substrate", data.get("substrate", "numerical")),
            ("Status", data.get("status", "experimental"))
        ])
        
        overview = TemplateEngine.render_section("Overview", 
            f"This experiment `{exp_id}` was executed by the Helix Orchestrator.")
        
        results = TemplateEngine.render_section("Results",
            f"Summary of findings extracted from artifacts.")
            
        return f"{infobox}\n{overview}\n{results}"

    @staticmethod
    def build_invariant_page(name: str, data: dict) -> str:
        infobox = TemplateEngine.render_infobox("Invariant", [
            ("Name", name),
            ("Confidence", str(data.get("confidence", "unknown"))),
            ("Occurrences", str(data.get("occurrences", 0)))
        ])
        
        desc = TemplateEngine.render_section("Description", 
            f"Structural invariant detected across multiple domains.")
            
        evidence = TemplateEngine.render_section("Evidence",
            "Supporting experiments:\n" + "\n".join([f"* [[experiments/{os.path.basename(p)}|{os.path.basename(p)}]]" for p in data.get("supporting_artifacts", [])]))
            
        return f"{infobox}\n{desc}\n{evidence}"
import os
