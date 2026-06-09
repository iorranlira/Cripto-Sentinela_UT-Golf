import paho.mqtt.client as mqtt
import json
import time
import logging

from config import ID_UNIDADE, BROKER, PORT

log = logging.getLogger(ID_UNIDADE)

TOPICO = f"sisdef/broadcast/chaves/{ID_UNIDADE}"

def publicar_identidade(identidade: dict) -> None:
    try:
        cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        cliente.connect(BROKER, PORT)
        cliente.loop_start()

        time.sleep(1)

        payload = json.dumps(identidade)
        cliente.publish(TOPICO, payload, retain=True)
        log.info(f"📡 Identidade publicada em: {TOPICO}")

        time.sleep(2)

    except Exception as e:
        log.error(f"❌ Erro ao publicar identidade: {e}")
    finally:
        cliente.loop_stop()
        cliente.disconnect()