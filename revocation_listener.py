import json
import logging
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
import paho.mqtt.client as mqtt
from config import BROKER, PORT, TOPICO_REVOGACAO
from uts_key_manager import carregar_chaves_confiadas, revogar_chave
from keys import load_ecdsa_pub_key

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("revocation-listener")


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        log.info(f"✅ Conectado ao Broker. Vigiando canal de revogação: {TOPICO_REVOGACAO}")
        client.subscribe(TOPICO_REVOGACAO)
    else:
        log.error(f"❌ Falha na conexão: {reason_code}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        remetente = payload.get("remetente")
        dados_revogacao = payload.get("revogacao")
        assinatura_b64 = payload.get("assinatura_b64")

        if not remetente or not dados_revogacao or not assinatura_b64:
            log.warning("⚠️ Recebido pacote de revogação incompleto. Ignorando.")
            return

        unidade_a_revogar = dados_revogacao.get("unidade_revogada")
        log.info(f"🔍 Recebida ordem de revogação para: {unidade_a_revogar} (emitida por {remetente})")

        chaves_confiadas = carregar_chaves_confiadas()

        if remetente not in chaves_confiadas and remetente != "oraculo":
            log.warning(f"⚠️ Revogação ignorada: remetente '{remetente}' não é uma unidade confiada.")
            return

        if remetente in chaves_confiadas:
            dados_remetente = chaves_confiadas[remetente]
            ecdsa_pub_b64 = dados_remetente.get("chave_publica_eddsa") or dados_remetente.get("chave_publica_ecdsa")

            if not ecdsa_pub_b64:
                log.error(f"❌ Não foi possível encontrar a chave ECDSA de {remetente}")
                return

            public_key = load_ecdsa_pub_key(ecdsa_pub_b64)
            assinatura = base64.b64decode(assinatura_b64)

            revogacao_json = json.dumps(dados_revogacao, separators=(',', ':')).encode()

            try:
                public_key.verify(
                    assinatura,
                    revogacao_json,
                    ec.ECDSA(hashes.SHA256())
                )
                log.info(f"✅ Assinatura de {remetente} validada. Ordem legítima.")
            except Exception:
                log.error(f"❌ Assinatura de revogação INVÁLIDA de {remetente}! Possível ataque da Sombra.")
                return

        revogar_chave(unidade_a_revogar)
        log.info(f"🚫 Unidade {unidade_a_revogar} foi banida da rede local.")

    except Exception as e:
        log.error(f"❌ Erro ao processar mensagem de revogação: {e}")


def main():
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    cliente.on_connect = on_connect
    cliente.on_message = on_message

    log.info("📡 Iniciando Sentinela de Revogação...")
    cliente.connect(BROKER, PORT)

    try:
        cliente.loop_forever()
    except KeyboardInterrupt:
        log.info("👋 Sentinela de revogação encerrada.")
        cliente.disconnect()


if __name__ == "__main__":
    main()
