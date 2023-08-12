from typing import Optional, List

def clean_strings(strings: List[str]) -> Optional[bytes]:
    s: str = "".join(strings)
    replace: List[str] = ["\n", "\r", "\t", "*"]
    if s is None:
        return None
    s = [s.replace(r, "") for r in replace]
    return bytes(s.strip(), "utf-8")