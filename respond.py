import paho.mqtt.client as mqtt
import json
import logging
import time
from config import ID_UNIDADE, BROKER, PORT, TOPICO_ORACULO

log = logging.getLogger(ID_UNIDADE)


def enviar_resposta(pacote: dict) -> bool:
    try:
        log.info(f"📤 Enviando resposta para o tópico: {TOPICO_ORACULO}")

        cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        cliente.connect(BROKER, PORT)
        cliente.loop_start()

        time.sleep(1)

        info = cliente.publish(TOPICO_ORACULO, json.dumps(pacote), qos=1)

        rc, mid = info.rc, info.mid
        log.info(f"⏳ Aguardando confirmação de envio (mid={mid})...")

        info.wait_for_publish(timeout=15)

        if info.is_published():
            log.info("✅ Resposta publicada e confirmada pelo broker")
            sucesso = True
        else:
            log.error("❌ Tempo esgotado ao aguardar confirmação de publicação")
            sucesso = False

        cliente.loop_stop()
        cliente.disconnect()
        return sucesso
    except Exception as e:
        log.error(f"❌ Falha ao enviar resposta: {e}")
        return False
