from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key().decode()

if __name__ == "__main__":
    key = generate_key()
    print("Generated Fernet Key:", key)
