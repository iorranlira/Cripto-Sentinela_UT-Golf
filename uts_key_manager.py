import json
import os
import logging
from datetime import datetime, timezone
from config import ID_UNIDADE
import paho.mqtt.client as mqtt
import time
from config import BROKER, PORT


log = logging.getLogger(ID_UNIDADE)

ARQUIVO_CHAVES_CONFIADAS = "chaves_confiadas.json"


def carregar_chaves_confiadas() -> dict:
    if os.path.exists(ARQUIVO_CHAVES_CONFIADAS):
        try:
            with open(ARQUIVO_CHAVES_CONFIADAS, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError):
            log.warning("⚠️ Arquivo de chaves confiadas corrompido — recriando...")
    return {}


def salvar_chaves_confiadas(chaves: dict) -> None:
    with open(ARQUIVO_CHAVES_CONFIADAS, "w") as f:
        json.dump(chaves, f, indent=2)


def adicionar_chave(id_unidade: str, rsa_pub: str, ecdsa_pub: str) -> None:
    if id_unidade == ID_UNIDADE:
        return  # não salva a si mesmo

    chaves = carregar_chaves_confiadas()
    chaves[id_unidade] = {
        "chave_publica_rsa":   rsa_pub,
        "chave_publica_ecdsa": ecdsa_pub,
        "ultima_atualizacao":  datetime.now(timezone.utc).isoformat()
    }
    salvar_chaves_confiadas(chaves)
    log.info(f"✅ Chave de {id_unidade} salva em {ARQUIVO_CHAVES_CONFIADAS}")


def buscar_chave(id_unidade: str) -> dict | None:
    chaves = carregar_chaves_confiadas()
    if id_unidade not in chaves:
        log.warning(f"⚠️ Chave de {id_unidade} não encontrada")
        return None
    return chaves[id_unidade]


def revogar_chave(id_unidade: str) -> None:
    chaves = carregar_chaves_confiadas()
    if id_unidade in chaves:
        del chaves[id_unidade]
        salvar_chaves_confiadas(chaves)
        log.info(f"🚫 Chave de {id_unidade} revogada")
    else:
        log.warning(f"⚠️ {id_unidade} não encontrada para revogar")

def listar_chaves_confiadas() -> None:
    chaves = carregar_chaves_confiadas()
    if not chaves:
        print("Nenhuma chave confiada salva")
        return
    print(f"\n{'='*50}")
    print(f"  {len(chaves)} unidade(s) confiada(s)")
    print(f"{'='*50}")
    for ut, dados in sorted(chaves.items()):
        print(f"\n  {ut.upper()}")
        print(f"  RSA    : {dados['chave_publica_rsa'][:40]}...")
        print(f"  ECDSA  : {dados['chave_publica_ecdsa'][:40]}...")
        print(f"  Salvo  : {dados['ultima_atualizacao']}")


def escanear_e_salvar_chaves() -> None:
    def on_connect(client, userdata, flags, reason_code, properties):
        client.subscribe("sisdef/broadcast/chaves/#")
        log.info("⏳ Escaneando broker...")

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            ut    = payload.get("id_unidade")
            rsa   = payload.get("chave_publica_rsa")
            ecdsa = payload.get("chave_publica_ecdsa")
            if ut and rsa and ecdsa:
                adicionar_chave(ut, rsa, ecdsa)
        except Exception as e:
            log.error(f"❌ Erro ao processar chave: {e}")

    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    cliente.on_connect = on_connect
    cliente.on_message = on_message
    cliente.connect(BROKER, PORT)
    cliente.loop_start()

    time.sleep(5)

    cliente.loop_stop()
    cliente.disconnect()
    log.info("✅ Escaneamento concluído")