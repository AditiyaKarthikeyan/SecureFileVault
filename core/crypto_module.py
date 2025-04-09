import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def load_rsa_key(file_path):
    print(f"[Crypto] Loading RSA key from {file_path}")
    with open(file_path, "rb") as key_file:
        if "private" in file_path:
            return serialization.load_pem_private_key(key_file.read(), password=None)
        else:
            return serialization.load_pem_public_key(key_file.read())

def encrypt_file(file_path, output_path=None):
    print("[Crypto] Starting encryption...")
    
    # Set default output path if not provided
    if output_path is None:
        output_dir = "assets/files/encrypted"
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(file_path)
        output_path = os.path.join(output_dir, f"{filename}.enc")
    
    # Verify input file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    # Verify output directory exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    public_key = load_rsa_key('assets/keys/public.pem')  # Changed to public.pem
    print("[Crypto] Loaded public key")

    with open(file_path, 'rb') as f:
        plaintext = f.read()
    print(f"[Crypto] Read plaintext of size: {len(plaintext)} bytes")

    # Generate random key and IV
    aes_key = os.urandom(32)
    iv = os.urandom(16)
    print("[Crypto] Generated AES key and IV")

    # Encrypt the data
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    print("[Crypto] AES encryption complete")

    # Encrypt the AES key with RSA
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print("[Crypto] RSA encryption of AES key complete")

    # Write to output file
    with open(output_path, 'wb') as f:
        f.write(len(encrypted_key).to_bytes(4, 'big'))
        f.write(encrypted_key)
        f.write(iv)
        f.write(ciphertext)
    print(f"[Crypto] Encrypted file written to: {output_path}")
    
    return output_path

def decrypt_file(file_path, output_path=None):
    print("[Crypto] Starting decryption...")
    
    # Set default output path if not provided
    if output_path is None:
        output_dir = "assets/files/decrypted"
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(file_path)
        if filename.endswith(".enc"):
            filename = filename[:-4]  # Remove .enc extension
        output_path = os.path.join(output_dir, filename)
    
    # Verify input file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    # Verify output directory exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    private_key = load_rsa_key('assets/keys/private.pem')  # Changed to private.pem
    print("[Crypto] Loaded private key")

    with open(file_path, 'rb') as f:
        key_len = int.from_bytes(f.read(4), 'big')
        encrypted_key = f.read(key_len)
        iv = f.read(16)
        ciphertext = f.read()
    print(f"[Crypto] Encrypted key length: {key_len}, ciphertext size: {len(ciphertext)}")

    # Decrypt the AES key with RSA
    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print("[Crypto] AES key recovered")

    # Decrypt the data
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    print("[Crypto] AES decryption complete")

    # Write to output file
    with open(output_path, 'wb') as f:
        f.write(plaintext)
    print(f"[Crypto] Decrypted file written to: {output_path}")
    
    return output_path
