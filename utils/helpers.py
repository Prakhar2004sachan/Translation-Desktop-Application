import hashlib
from typing import List

def get_hash(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def contains_uuid(text: str) -> bool:
    import re
    uuid_pattern = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)
    return bool(uuid_pattern.search(text))
