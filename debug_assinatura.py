import base64
import hashlib
import json
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from keys import load_ecdsa_pub_key, load_rsa_priv_key, carregar_ou_gerar_chaves
from config import ORACULO_ECDSA_PUB_B64

pacote = {
  "id_unidade": "oraculo",
  "ciphertext_b64": "zeMjaFg4PiwqZevo7zNPEmV2jXbpyLzrromBS0lnj3Hgd8NCf7rWgphe8NXVdQFBsbBaeAgxafipDrzi",
  "tag_autenticacao_b64": "NyHJUjSVrMMnikLX+l8/1w==",
  "nonce_b64": "Yme5qTcNqoze7gkP",
  "chave_sessao_cifrada_b64": "aOk+zFOXPWQCh/PPMbpHPgIsB8XNo5QkUgEHRixFPyTKzu3thJtsUR3+Tn6jM6piaGSwvZ5Q4yVxT0ZbTBd3gFk9QXWNjeOcsKhKwsBkESWJPCke/QCJLnGP7p3Kwd8zyP9/9COAKcxJBvX/FRXfvNIB7S5qqh4R1mzJWBwXPYF2Kt2HUxyKaXotxKiUKpo6t8zgACri7QKRspUpYXHKFz6FPTc8Y/Rm8PML6tsx/N1Zdw058RY2+vmJm+5un0NNjRNKo8p3UO/JqUr3Ymd/lWv/+FwTarHCQQsJG3dmJyE92cBqXj3O2th7crVw1UrCKcVBhiRkkaLykPQYOrkEHg==",
  "assinatura_b64": "MEYCIQD8aNuxyNPGAx+NZ3HHTkf3dliC0RIhgFqf2r4ddNpC9AIhAPCRFMmA2zAMi1kLY6DHvDAf7nPYmBbu2snSHLdAcLTS"
}

oraculo_ecdsa_pub = load_ecdsa_pub_key(ORACULO_ECDSA_PUB_B64)
assinatura             = base64.b64decode(pacote["assinatura_b64"])
ciphertext             = base64.b64decode(pacote["ciphertext_b64"])
tag                    = base64.b64decode(pacote["tag_autenticacao_b64"])
nonce                  = base64.b64decode(pacote["nonce_b64"])
chave_sessao_cifrada   = base64.b64decode(pacote["chave_sessao_cifrada_b64"])

# ── Decifrar chave de sessão ────────────────────────────────────
chaves = carregar_ou_gerar_chaves()
rsa_priv = load_rsa_priv_key(chaves["rsa"]["private_key"])

try:
    chave_sessao = rsa_priv.decrypt(
        chave_sessao_cifrada,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print(f"✅ Chave de sessão decifrada: {chave_sessao.hex()[:20]}...")
except Exception as e:
    print(f"❌ Falha ao decifrar chave de sessão: {e}")
    exit()

# ── Decifrar mensagem ───────────────────────────────────────────
try:
    aesgcm    = AESGCM(chave_sessao)
    plaintext = aesgcm.decrypt(nonce, ciphertext + tag, None)
    print(f"✅ Plaintext decifrado: {plaintext}")
except Exception as e:
    print(f"❌ Falha ao decifrar mensagem: {e}")
    exit()

# ── Testar assinatura sobre o plaintext ─────────────────────────
candidatos = {
    "plaintext":               plaintext,
    "plaintext (string)":      plaintext.decode().encode(),
    "hash sha256 do plaintext": hashlib.sha256(plaintext).digest(),
}

for nome, dado in candidatos.items():
    try:
        oraculo_ecdsa_pub.verify(assinatura, dado, ec.ECDSA(hashes.SHA256()))
        print(f"✅ ACHOU! Método: SHA256 direto | Dado: {nome}")
        continue
    except:
        pass

    try:
        h = hashlib.sha256(dado).digest()
        oraculo_ecdsa_pub.verify(assinatura, h, ec.ECDSA(hashes.Prehashed()))
        print(f"✅ ACHOU! Método: Prehashed | Dado: {nome}")
        continue
    except:
        pass

    print(f"❌ Falhou: {nome}")