from typing import Optional, List

def clean_strings(strings: List[str]) -> Optional[bytes]:
    s: str = "".join(strings)
    if s is None:
        return None
    return bytes(s.replace("\n", "").replace("\r", "").replace("\t", "").strip(), "utf-8")