import hashlib

def test_password_hash(password):
    """
    Test utility to generate a SHA-256 hash for a password
    Usage: python -c "from utils import test_password_hash; test_password_hash('your_password')"
    """
    hashed = hashlib.sha256(password.encode()).hexdigest()
    print(f"Password: {password}")
    print(f"SHA-256 Hash: {hashed}")
    return hashed

if __name__ == "__main__":
    # Example usage
    test_password = "admin123"
    test_password_hash(test_password)
