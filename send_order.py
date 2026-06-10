import json
import logging
from config import BROKER, PORT
from uts_key_manager import carregar_chaves_confiadas, listar_chaves_confiadas
from keys import load_rsa_pub_key
from encrypt import cifrar_mensagem

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("send-order")


def main():
    chaves_uteis = carregar_chaves_confiadas()

    if not chaves_uteis:
        log.warning("⚠️ Nenhuma unidade confiada encontrada. Rode o 'main.py' primeiro para escanear a rede.")
        return

    print("\n--- 🛰️ CENTRAL DE COMANDO: ENVIO DE ORDENS ---")
    listar_chaves_confiadas()

    destino = input("\n🎯 Digite o codinome da UT de destino (ex: ut-alfa): ").strip().lower()

    if destino not in chaves_uteis:
        log.error(f"❌ Unidade '{destino}' não está na sua lista de confiança!")
        return

    ordem = input(f"📝 Digite a ordem para {destino.upper()}: ").strip()

    if not ordem:
        log.warning("⚠️ Ordem vazia. Operação cancelada.")
        return

    try:
        log.info(f"🔐 Preparando criptografia para {destino}...")
        rsa_pub_b64 = chaves_uteis[destino]["chave_publica_rsa"]
        rsa_pub = load_rsa_pub_key(rsa_pub_b64)

        pacote = cifrar_mensagem(ordem, rsa_pub)

        if pacote:
            topico_destino = f"sisdef/direto/{destino}"

            import paho.mqtt.client as mqtt
            import time

            log.info(f"📤 Enviando pacote seguro para {topico_destino}...")
            cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            cliente.connect(BROKER, PORT)
            cliente.loop_start()

            time.sleep(1)
            info = cliente.publish(topico_destino, json.dumps(pacote), qos=1)
            info.wait_for_publish(timeout=10)

            if info.is_published():
                log.info(f"✅ Ordem enviada com sucesso para {destino.upper()}!")
            else:
                log.error("❌ Falha ao confirmar envio com o broker.")

            cliente.loop_stop()
            cliente.disconnect()
        else:
            log.error("❌ Falha ao gerar pacote criptográfico.")

    except Exception as e:
        log.error(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    main()
