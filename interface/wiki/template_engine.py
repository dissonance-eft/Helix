from __future__ import annotations

class TemplateEngine:
    """
    Wikipedia-style template engine for Helix Wiki.
    """
    
    @staticmethod
    def render_infobox(title: str, pairs: list[tuple[str, str]]) -> str:
        lines = [
            "{| class=\"infobox\" style=\"width:22em; border:1px solid #aaa; background-color:#f9f9f9; padding:5px; margin:0.5em 0 0.5em 1em; float:right;\"",
            f"|+ style=\"background-color:#eee; font-weight:bold;\" | {title}",
            "|-"
        ]
        for key, value in pairs:
            lines.append(f"! {key}")
            lines.append(f"| {value}")
            lines.append("|-")
        lines.append("|}")
        return "\n".join(lines)

    @staticmethod
    def render_section(title: str, content: str) -> str:
        return f"== {title} ==\n{content}\n"

    @staticmethod
    def format_link(text: str, target: str) -> str:
        return f"[[{target}|{text}]]"
