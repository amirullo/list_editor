import uuid

def generate_uuid() -> str:
    """
    Generate a new UUID string
    """
    return str(uuid.uuid4())