# enviar_resposta.py
import json
import base64
import os
import paho.mqtt.client as mqtt
from cryptography.hazmat.primitives.asymmetric import padding, ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import ID_UNIDADE, BROKER, PORT, ORACULO_RSA_PUB_B64
from keys import carregar_ou_gerar_chaves, load_rsa_pub_key, load_ecdsa_priv_key

def main():
    print(f"[*] Preparando envio do Passo 3 - Unidade: {ID_UNIDADE.lower()}")

    chaves = carregar_ou_gerar_chaves()
    oraculo_rsa_pub = load_rsa_pub_key(ORACULO_RSA_PUB_B64)
    minha_ecdsa_priv_obj = load_ecdsa_priv_key(chaves["ecdsa"]["private_key"])

    resposta_usuario = input("\nDigite apenas o número resultado do desafio: ").strip()
    mensagem_bytes = resposta_usuario.encode('utf-8')

    chave_sessao = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(chave_sessao)
    nonce = os.urandom(12)
    
    ciphertext = aesgcm.encrypt(nonce, mensagem_bytes, associated_data=None)
    tag = ciphertext[-16:]
    pure_ciphertext = ciphertext[:-16]

    chave_sessao_cifrada = oraculo_rsa_pub.encrypt(
        chave_sessao,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    assinatura = minha_ecdsa_priv_obj.sign(
        mensagem_bytes,
        ec.ECDSA(hashes.SHA256())
    )

    pacote = {
        "id_unidade": ID_UNIDADE,
        "cmd": "resposta",
        "ciphertext_b64": base64.b64encode(pure_ciphertext).decode('utf-8'),
        "tag_autenticacao_b64": base64.b64encode(tag).decode('utf-8'),
        "nonce_b64": base64.b64encode(nonce).decode('utf-8'),
        "chave_sessao_cifrada_b64": base64.b64encode(chave_sessao_cifrada).decode('utf-8'),
        "assinatura_b64": base64.b64encode(assinatura).decode('utf-8')
    }

    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    cliente.connect(BROKER, PORT)
    cliente.publish("sisdef/direto/oraculo", json.dumps(pacote))
    cliente.disconnect()

    print("\n[✅ SUCESSO] Passo 3 executado: Resposta enviada ao Oráculo!")

if __name__ == "__main__":
    main()
