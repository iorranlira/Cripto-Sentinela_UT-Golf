from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import serialization
import base64
import json

#RSA KEYS
rsa_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
rsa_public_key = rsa_private_key.public_key()

#ECDSA KEYS
ecdsa_private_key = ec.generate_private_key(ec.SECP256R1())
ecdsa_public_key = ecdsa_private_key.public_key()

# Condificando keys em Base64
def export_keys_as_string(private_key, public_key):
    _priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    _pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return {
        "private_key": base64.b64encode(_priv_bytes).decode(),
        "public_key":  base64.b64encode(_pub_bytes).decode()
    }

def load_rsa_pub_key(b64_str):
    return serialization.load_der_public_key(base64.b64decode(b64_str))

def load_ecdsa_pub_key(b64_str):
    return serialization.load_der_public_key(base64.b64decode(b64_str))

chaves_rsa   = export_keys_as_string(rsa_private_key, rsa_public_key)
chaves_ecdsa = export_keys_as_string(ecdsa_private_key, ecdsa_public_key)

ID_UNIDADE = "ut-golf"

identidade = {
    "id_unidade": ID_UNIDADE,
   "chave_publica_rsa":   chaves_rsa["public_key"],
    "chave_publica_ecdsa": chaves_ecdsa["public_key"]
}

print(json.dumps(identidade, indent=2))
print(f"RSA  privada : {chaves_rsa['private_key'][:40]}...")