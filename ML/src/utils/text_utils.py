def build_text(*parts: str) -> str:
    clean = [p.strip() for p in parts if isinstance(p, str) and p.strip()]
    return "\n\n".join(clean)