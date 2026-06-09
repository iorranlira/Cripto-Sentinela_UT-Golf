import paho.mqtt.client as mqtt
import time
import json
from config import ID_UNIDADE

unidades = {}

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("sisdef/broadcast/chaves/#")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        ut = payload.get("id_unidade", msg.topic.split("/")[-1])
        unidades[ut] = {
            "topico":  msg.topic,
            "rsa":     payload.get("chave_publica_rsa",   "")[:40] + "...",
            "ecdsa":   payload.get("chave_publica_ecdsa", "")[:40] + "..."
        }
    except Exception as e:
        print(f"❌ Erro ao processar {msg.topic}: {e}")

cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.on_connect = on_connect
cliente.on_message = on_message
cliente.connect("broker.hivemq.com", 1883)
cliente.loop_start()

print("⏳ Escaneando broker...")
time.sleep(5)
cliente.loop_stop()
cliente.disconnect()

print(f"\n{'='*50}")
print(f"  {len(unidades)} unidade(s) encontrada(s) no broker")
print(f"{'='*50}")

for ut, dados in sorted(unidades.items()):
    marcador = "👉" if ut == ID_UNIDADE else "  "
    print(f"\n{marcador} {ut.upper()}")
    print(f"   Tópico : {dados['topico']}")
    print(f"   RSA    : {dados['rsa']}")
    print(f"   ECDSA  : {dados['ecdsa']}")

print(f"\n{'='*50}")
if ID_UNIDADE in unidades:
    print(f"✅ Sua identidade ({ID_UNIDADE}) está presente")
else:
    print(f"❌ Sua identidade ({ID_UNIDADE}) NÃO está no broker")
    print("→ Rode python3 main.py para publicar")