import json
import logging
from cryptography.fernet import Fernet


class EncryptionHandler:
    def __init__(self, key_file_path):
        self.key_file_path = key_file_path
        self.fernet_key = None

    def generate_key(self):
        try:
            self.fernet_key = Fernet.generate_key()
            with open(self.key_file_path, "wb") as key_file:
                key_file.write(self.fernet_key)
        except Exception as e:
            logging.error(f"Error occurred while generating encryption key: {e}")

    def load_key(self):
        try:
            with open(self.key_file_path, "rb") as key_file:
                self.fernet_key = key_file.read()
        except FileNotFoundError:
            logging.error(f"Encryption key file not found: {self.key_file_path}")
        except Exception as e:
            logging.error(f"Error occurred while loading encryption key: {e}")

    def encrypt_config(self, config, encrypted_file_path):
        try:
            if self.fernet_key is None:
                logging.error("Encryption key not loaded.")
                return

            fernet = Fernet(self.fernet_key)
            encrypted_config = fernet.encrypt(json.dumps(config).encode())

            with open(encrypted_file_path, "wb") as encrypted_file:
                encrypted_file.write(encrypted_config)
        except Exception as e:
            logging.error(f"Error occurred while encrypting configuration: {e}")

    def decrypt_config(self, encrypted_file_path):
        try:
            if self.fernet_key is None:
                logging.error("Encryption key not loaded.")
                return

            with open(encrypted_file_path, "rb") as encrypted_file:
                encrypted_config = encrypted_file.read()

            fernet = Fernet(self.fernet_key)
            decrypted_config = fernet.decrypt(encrypted_config).decode()

            return json.loads(decrypted_config)
        except Exception as e:
            logging.error(f"Error occurred while decrypting configuration: {e}")
            return None
