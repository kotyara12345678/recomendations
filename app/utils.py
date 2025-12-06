import re

CLOSE_RE = re.compile(r"\b(?:close[sd]?|fix(?:es)?|resolve[sd]?)\s+(?:#(\d+)|https?://\S+/issues/(\d+))", re.I)
REF_RE = re.compile(r"#(\d+)")

def extract_refs(text: str):

    nums = set()
    if not text:
        return []
    for m in CLOSE_RE.finditer(text):
        g1 = m.group(1) or m.group(2)
        if g1:
            nums.add(int(g1))
    for m in REF_RE.finditer(text):
        nums.add(int(m.group(1)))
    return sorted(nums)