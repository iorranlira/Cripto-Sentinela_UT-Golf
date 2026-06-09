import paho.mqtt.client as mqtt
import json
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("ut-golf")

ORACULO_RSA_PUB_B64   = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0JYEsxupPYOio+u8xHdzSNLQgQoPwFx/qceHQJPy2KzNSCXz3FFyKkXaso4UTorzy8XXDv5WkRC1AlDDVu28ANXlrZqLyjLZ8DdplHig2KSxYV5MXA5TyqMDeCAW5CWi+na5Xwr9IbtuTfCv65YeB3QRgZWjZ4oVxpGVek+4dec0qChNl6pL9KmgI4u5CHHC8d7z6MovK0+eN0aMIT2bWgri29tT9sDCoHEGaab1576+SXK3iDXlLkeehJ/h72lqu3HmSL/B5ZE+pKLVLJogSwwMCTejrfTXf5acj9EOq83wGNLTjHIKr2iMz+SZzFS4vxk6qMgltCXjBZfXalzLnwIDAQAB"
ORACULO_ECDSA_PUB_B64 = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEfmgdDET1IKOR2OxLI9KBBzFB97GyrJKipAuwSrMhDn1w93ieoCb7etbYX5/wrUic9xX5LQbUdgyKSRuCnTPAeQ=="

oraculo_rsa_pub   = load_rsa_pub_key(ORACULO_RSA_PUB_B64)
oraculo_ecdsa_pub = load_ecdsa_pub_key(ORACULO_ECDSA_PUB_B64)
log.info("✅ Chaves públicas do Oráculo carregadas")

BROKER          = "broker.hivemq.com"
PORT            = 1883
TOPICO_ORACULO  = "sisdef/direto/oraculo"
TOPICO_RESPOSTA = f"sisdef/direto/{ID_UNIDADE}"

mensagem_oraculo = None

CAMPOS_OBRIGATORIOS = [
    "ciphertext_b64",
    "tag_autenticacao_b64",
    "nonce_b64",
    "chave_sessao_cifrada_b64",
    "assinatura_b64"
]

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
            log.info(f"Escutando em: {TOPICO_RESPOSTA}")
        else:
            log.error(f"❌ Falha na conexão — código: {reason_code}")
    except Exception as e:
        log.error(f"❌ Erro no on_connect: {e}")

def on_message(client, userdata, msg):
    global mensagem_oraculo
    try:
        log.info(f"📨 Mensagem recebida no tópico: {msg.topic}")
        print(f"\n📨 Tópico: {msg.topic}")
        print(f"Payload bruto: {msg.payload.decode()}")
        try:
            pacote = json.loads(msg.payload.decode())
        except json.JSONDecodeError as e:
            log.error(f"❌ Payload não é um JSON válido — rejeitando. Erro: {e}")
            return

        if not validar_pacote(pacote):
            log.warning("⚠️ Mensagem rejeitada por formato inválido")
            return

        mensagem_oraculo = pacote
        log.info("✅ Pacote válido recebido e armazenado")
        print(json.dumps(mensagem_oraculo, indent=2))

    except Exception as e:
        log.error(f"❌ Erro inesperado ao processar mensagem — rejeitando. Erro: {e}")

try:
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    cliente.on_connect = on_connect
    cliente.on_message = on_message

    cliente.connect(BROKER, PORT)
    cliente.loop_start()
    time.sleep(2)

except Exception as e:
    log.error(f"❌ Erro ao inicializar cliente MQTT: {e}")
    raise

try:
    pedido = {
        "id_unidade": ID_UNIDADE,
        "cmd": "desafio"
    }

    cliente.publish(TOPICO_ORACULO, json.dumps(pedido))
    log.info(f"📤 Desafio solicitado ao Oráculo")

except Exception as e:
    log.error(f"❌ Erro ao publicar pedido de desafio: {e}")

log.info("⏳ Aguardando resposta do Oráculo...")
time.sleep(10)

cliente.loop_stop()
cliente.disconnect()

if mensagem_oraculo:
    log.info("✅ Pronto para o Passo 2 — mensagem_oraculo disponível")
    print("✅ Pronto para o Passo 2!")
    print(json.dumps(mensagem_oraculo, indent=2))
else:
    log.warning("⚠️ Nenhuma resposta recebida — tente rodar novamente")