import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import serialization

ARQUIVO_CHAVES_LOCAIS = "minhas_chaves.json"

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

def load_rsa_priv_key(b64_str):
    return serialization.load_der_private_key(base64.b64decode(b64_str), password=None)

def load_ecdsa_priv_key(b64_str):
    return serialization.load_der_private_key(base64.b64decode(b64_str), password=None)

def gerar_e_salvar_chaves():
    rsa_priv   = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ecdsa_priv = ec.generate_private_key(ec.SECP256R1())

    chaves = {
        "rsa":   export_keys_as_string(rsa_priv, rsa_priv.public_key()),
        "ecdsa": export_keys_as_string(ecdsa_priv, ecdsa_priv.public_key())
    }

    with open(ARQUIVO_CHAVES_LOCAIS, "w") as f:
        json.dump(chaves, f, indent=2)

    return chaves

def carregar_ou_gerar_chaves():
    if os.path.exists(ARQUIVO_CHAVES_LOCAIS):
        with open(ARQUIVO_CHAVES_LOCAIS, "r") as f:
            chaves = json.load(f)
        print("✅ Chaves carregadas do arquivo")
    else:
        chaves = gerar_e_salvar_chaves()
        print("✅ Chaves geradas e salvas em", ARQUIVO_CHAVES_LOCAIS)
    return chaves