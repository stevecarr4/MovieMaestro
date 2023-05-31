import json
import logging
import os
from cryptography.fernet import Fernet


def generate_default_config(config_file_path):
    default_config = {
        "MOVIE_API_KEY": "YOUR_MOVIE_API_KEY",
        "TICKETING_SYSTEM_AUTH_TOKEN": "YOUR_TICKETING_SYSTEM_AUTH_TOKEN",
        "EMAIL_SERVICE_AUTH_TOKEN": "YOUR_EMAIL_SERVICE_AUTH_TOKEN"
    }

    try:
        with open(config_file_path, "w") as config_file:
            json.dump(default_config, config_file, indent=4)
    except Exception as e:
        logging.error(f"Error occurred while generating default config file: {e}")


def load_config(config_file_path):
    try:
        with open(config_file_path, "r") as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        logging.error(f"Config file not found: {config_file_path}")
        return None
    except Exception as e:
        logging.error(f"Error occurred while loading config file: {e}")
        return None


def encrypt_config(config, encryption_key):
    try:
        fernet = Fernet(encryption_key)
        encrypted_config = fernet.encrypt(json.dumps(config).encode())
        return encrypted_config
    except Exception as e:
        logging.error(f"Error occurred while encrypting config: {e}")
        return None


def decrypt_config(encrypted_config, encryption_key):
    try:
        fernet = Fernet(encryption_key)
        decrypted_config = fernet.decrypt(encrypted_config).decode()
        return json.loads(decrypted_config)
    except Exception as e:
        logging.error(f"Error occurred while decrypting config: {e}")
        return None


def generate_encryption_key(key_file_path):
    try:
        if not os.path.exists(key_file_path):
            encryption_key = Fernet.generate_key()
            with open(key_file_path, "wb") as key_file:
                key_file.write(encryption_key)
    except Exception as e:
        logging.error(f"Error occurred while generating encryption key: {e}")


def load_encryption_key(key_file_path):
    try:
        with open(key_file_path, "rb") as key_file:
            encryption_key = key_file.read()
        return encryption_key
    except FileNotFoundError:
        logging.error(f"Encryption key file not found: {key_file_path}")
        return None
    except Exception as e:
        logging.error(f"Error occurred while loading encryption key: {e}")
        return None
