import os
from cryptography.fernet import Fernet
from app.models import Address, db
from sqlalchemy.orm import load_only

class AddressEncryptionService:
    BATCH_SIZE = 1000

    def __init__(self):
        self.DB_ENCRYPTION_KEY = self.get_or_generate_key()

    def get_or_generate_key(self):
        key = os.environ.get('DB_ENCRYPTION_KEY')
        if not key:
            raise ValueError("DB_ENCRYPTION_KEY not set in the environment")
        return key

    def process_address(self, mode='encrypt'):
        total_processed = 0
        query = Address.query.options(load_only('id', '_address_line_1', '_address_line_2', '_city', '_state', '_zip_code'))
        total_addresses = query.count()
        
        for offset in range(0, total_addresses, self.BATCH_SIZE):
            addresses = query.limit(self.BATCH_SIZE).offset(offset).all()
            for address in addresses:
                self._process_address(address, mode)
            db.session.commit()
            total_processed += len(addresses)
            print(f'Processed {total_processed} / {total_addresses} addresses')

    def _process_address(self, address, mode):
        try:
            fields = ['_address_line_1', '_address_line_2', '_city', '_state', '_zip_code']
            for field in fields:
                current_value = getattr(address, field)
                if mode == 'encrypt' and not self._is_encrypted(current_value):
                    setattr(address, field, self.encrypt_data(current_value))
                elif mode == 'decrypt' and self._is_encrypted(current_value):
                    setattr(address, field, self.decrypt_data(current_value))
        except Exception as e:
            print(f'Error processing address {address.id}: {e}')

    def encrypt_data(self, data):
        if data is None:
            return None
        fernet = Fernet(self.DB_ENCRYPTION_KEY)
        return fernet.encrypt(data.encode()).decode()

    def decrypt_data(self, data):
        if data is None:
            return None
        fernet = Fernet(self.DB_ENCRYPTION_KEY)
        return fernet.decrypt(data.encode()).decode()

# Usage
address_service = AddressEncryptionService()
address_service.process_address(mode='encrypt')
