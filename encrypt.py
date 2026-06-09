import base64
import os
import logging
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import ID_UNIDADE
from keys import carregar_ou_gerar_chaves, load_ecdsa_priv_key

log = logging.getLogger(ID_UNIDADE)


def cifrar_mensagem(plaintext: str, oraculo_rsa_pub) -> dict | None:
    try:
        plaintext_bytes = plaintext.encode()

        log.info("🔑 Gerando chave de sessão AES...")
        chave_sessao = AESGCM.generate_key(bit_length=256)

        log.info("📨 Cifrando resposta com AES-GCM...")
        aesgcm = AESGCM(chave_sessao)
        nonce = os.urandom(12)
        ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext_bytes, None)

        tag = ciphertext_with_tag[-16:]
        ciphertext = ciphertext_with_tag[:-16]

        log.info("🔑 Cifrando chave de sessão com RSA do Oráculo...")
        chave_sessao_cifrada = oraculo_rsa_pub.encrypt(
            chave_sessao,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        log.info("✍️ Assinando resposta com ECDSA...")
        chaves = carregar_ou_gerar_chaves()
        ecdsa_priv = load_ecdsa_priv_key(chaves["ecdsa"]["private_key"])
        assinatura = ecdsa_priv.sign(
            plaintext_bytes,
            ec.ECDSA(hashes.SHA256())
        )

        pacote = {
            "id_unidade": ID_UNIDADE,
            "cmd": "resposta",
            "ciphertext_b64": base64.b64encode(ciphertext).decode(),
            "tag_autenticacao_b64": base64.b64encode(tag).decode(),
            "nonce_b64": base64.b64encode(nonce).decode(),
            "chave_sessao_cifrada_b64": base64.b64encode(chave_sessao_cifrada).decode(),
            "assinatura_b64": base64.b64encode(assinatura).decode()
        }

        log.info("✅ Resposta cifrada e assinada com sucesso")
        return pacote

    except Exception as e:
        log.error(f"❌ Erro ao cifrar mensagem: {e}")
        return None
