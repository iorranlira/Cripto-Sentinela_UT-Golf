import paho.mqtt.client as mqtt
import json
import time
import logging

from config import (
    ID_UNIDADE, BROKER, PORT,
    TOPICO_ORACULO, TOPICO_RESPOSTA,
    CAMPOS_OBRIGATORIOS
)

log = logging.getLogger("ut-golf")

def validar_pacote(pacote: dict) -> bool:
    faltando = [c for c in CAMPOS_OBRIGATORIOS if c not in pacote]
    if faltando:
        log.error(f"❌ Pacote inválido — campos ausentes: {faltando}")
        return False
    return True

def on_connect(client, userdata, flags, reason_code, properties):
    try:
        if reason_code == 0:
            log.info("✅ Conectado ao broker")
            client.subscribe(TOPICO_RESPOSTA)
            log.info(f"👂 Escutando em: {TOPICO_RESPOSTA}")
        else:
            log.error(f"❌ Falha na conexão — código: {reason_code}")
    except Exception as e:
        log.error(f"❌ Erro no on_connect: {e}")

def on_message(client, userdata, msg):
    try:
        log.info(f"📨 Mensagem recebida no tópico: {msg.topic}")

        try:
            pacote = json.loads(msg.payload.decode())
        except json.JSONDecodeError as e:
            log.error(f"❌ Payload não é JSON válido — rejeitando. Erro: {e}")
            return

        if not validar_pacote(pacote):
            log.warning("⚠️ Mensagem rejeitada por formato inválido")
            return

        userdata["mensagem_oraculo"] = pacote
        log.info("✅ Pacote válido recebido e armazenado")

    except Exception as e:
        log.error(f"❌ Erro inesperado ao processar mensagem: {e}")

def solicitar_desafio() -> dict | None:
    estado = {"mensagem_oraculo": None}

    try:
        cliente = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            userdata=estado
        )
        cliente.on_connect = on_connect
        cliente.on_message = on_message

        cliente.connect(BROKER, PORT)
        cliente.loop_start()
        time.sleep(2)

        pedido = {"id_unidade": ID_UNIDADE, "cmd": "desafio"}
        cliente.publish(TOPICO_ORACULO, json.dumps(pedido))
        log.info("📤 Desafio solicitado ao Oráculo")

        log.info("⏳ Aguardando resposta do Oráculo...")
        time.sleep(10)

    except Exception as e:
        log.error(f"❌ Erro ao solicitar desafio: {e}")
    finally:
        cliente.loop_stop()
        cliente.disconnect()

    return estado["mensagem_oraculo"]