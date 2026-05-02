import hashlib, uuid

def generate_cache_key(*args) -> str:
    raw = ":".join(str(a) for a in args)
    return hashlib.md5(raw.encode()).hexdigest()

def generate_uuid() -> str:
    return str(uuid.uuid4())
