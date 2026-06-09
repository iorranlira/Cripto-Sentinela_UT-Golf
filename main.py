import logging
import json
import paho.mqtt.client as mqtt
from uts_key_manager import escanear_e_salvar_chaves, listar_chaves_confiadas
from config import (
    ID_UNIDADE,
    ORACULO_RSA_PUB_B64,
    ORACULO_ECDSA_PUB_B64
)
from keys import (
    carregar_ou_gerar_chaves,
    load_rsa_pub_key,
    load_ecdsa_pub_key
)
from identity import publicar_identidade
from challenge import solicitar_desafio
from decrypt import decifrar_mensagem

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(ID_UNIDADE)

def main():

    # Carregar chaves locais
    chaves = carregar_ou_gerar_chaves()
    log.info("✅ Chaves locais carregadas")

    # Carregar chaves públicas do Oráculo
    oraculo_rsa_pub   = load_rsa_pub_key(ORACULO_RSA_PUB_B64)
    oraculo_ecdsa_pub = load_ecdsa_pub_key(ORACULO_ECDSA_PUB_B64)
    log.info("✅ Chaves públicas do Oráculo carregadas")

    # Montar identidade
    identidade = {
        "id_unidade":          ID_UNIDADE,
        "chave_publica_rsa":   chaves["rsa"]["public_key"],
        "chave_publica_ecdsa": chaves["ecdsa"]["public_key"]
    }

    # Publicar identidade no broker
    publicar_identidade(identidade)

    # Escanear broker e salvar chaves das outras UTs
    escanear_e_salvar_chaves()
    listar_chaves_confiadas()

    # Solicitar e receber desafio do Oráculo
    mensagem_oraculo = solicitar_desafio()

    if mensagem_oraculo:
        log.info("✅ Desafio recebido!")
        print(json.dumps(mensagem_oraculo, indent=2))
    else:
        log.warning("⚠️ Nenhuma resposta recebida — tente rodar novamente")

    if mensagem_oraculo:
        pergunta = decifrar_mensagem(mensagem_oraculo, oraculo_ecdsa_pub)
        if pergunta:
            print(f"\n❓ Pergunta do Oráculo: {pergunta}")

if __name__ == "__main__":
    main()