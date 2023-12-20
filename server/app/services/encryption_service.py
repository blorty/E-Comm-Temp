import os
from cryptography.fernet import Fernet
from app.models import Address, db
from sqlalchemy.orm import load_only

class AddressEncryptionService:
    BATCH_SIZE = 1000
    
    def __init__(self, DB_ENCRYPTION_KEY):
        self.DB_ENCRYPTION_KEY = DB_ENCRYPTION_KEY
        
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
        # This function now directly interacts with the encrypted fields
        try:
            fields = ['_address_line_1', '_address_line_2', '_city', '_state', '_zip_code']
            for field in fields:
                current_value = getattr(address, field)
                if mode == 'encrypt' and not self._is_encrypted(current_value):
                    # Directly set encrypted data
                    setattr(address, field, address.encrypt_field(current_value))
                elif mode == 'decrypt' and self._is_encrypted(current_value):
                    # Directly set decrypted data
                    setattr(address, field, address.decrypt_field(current_value))
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
encryption_key = os.environ.get('DB_ENCRYPTION_KEY')
address_service = AddressEncryptionService(encryption_key)
address_service.process_address(mode='encrypt')
