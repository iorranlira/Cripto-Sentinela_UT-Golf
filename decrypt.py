# decrypt.py

import base64
import hashlib
import logging
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import ID_UNIDADE
from keys import carregar_ou_gerar_chaves, load_rsa_priv_key

log = logging.getLogger(ID_UNIDADE)

def decifrar_mensagem(pacote: dict, oraculo_ecdsa_pub) -> str | None:
    try:
        # Decodificar campos Base64
        ciphertext           = base64.b64decode(pacote["ciphertext_b64"])
        tag                  = base64.b64decode(pacote["tag_autenticacao_b64"])
        nonce                = base64.b64decode(pacote["nonce_b64"])
        chave_sessao_cifrada = base64.b64decode(pacote["chave_sessao_cifrada_b64"])
        assinatura           = base64.b64decode(pacote["assinatura_b64"])

        # Decifrar chave de sessão com RSA privada 
        log.info("🔑 Decifrando chave de sessão...")
        try:
            chaves   = carregar_ou_gerar_chaves()
            rsa_priv = load_rsa_priv_key(chaves["rsa"]["private_key"])
            chave_sessao = rsa_priv.decrypt(
                chave_sessao_cifrada,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            log.info("✅ Chave de sessão decifrada")
        except Exception as e:
            log.error(f"❌ Falha ao decifrar chave de sessão: {e}")
            return None

        # Decifrar mensagem com AES-GCM
        log.info("📨 Decifrando mensagem...")
        try:
            aesgcm    = AESGCM(chave_sessao)
            plaintext = aesgcm.decrypt(nonce, ciphertext + tag, None)
            log.info("✅ Mensagem decifrada")
        except Exception as e:
            log.error(f"❌ Falha ao decifrar mensagem: {e}")
            return None

        # Verificar assinatura ECDSA do Oráculo
        log.info("🔍 Verificando assinatura do Oráculo...")
        try:
            oraculo_ecdsa_pub.verify(
                assinatura,
                plaintext,
                ec.ECDSA(hashes.SHA256())
            )
            log.info("✅ Assinatura válida — mensagem autêntica")
        except Exception:
            log.error("❌ Assinatura inválida — mensagem rejeitada")
            return None

        return plaintext.decode()

    except Exception as e:
        log.error(f"❌ Erro inesperado: {e}")
        return None