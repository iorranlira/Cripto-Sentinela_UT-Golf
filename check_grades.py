import json
import time
import paho.mqtt.client as mqtt
from config import BROKER, PORT, TOPICO_NOTAS


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("[*] Connected to Broker. Listening and requesting grades...")
        client.subscribe(TOPICO_NOTAS)

        payload = {"cmd": "atualizar_notas"}
        client.publish(TOPICO_NOTAS, json.dumps(payload))
    else:
        print(f"[-] Connection failed. Code: {reason_code}")


def on_message(client, userdata, msg):
    try:
        dados = json.loads(msg.payload.decode('utf-8'))
        print(json.dumps(dados, indent=2))
    except Exception as e:
        print(f"[-] Error processing data: {e}")


def main():
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    cliente.on_connect = on_connect
    cliente.on_message = on_message

    cliente.connect(BROKER, PORT)

    print(f"[*] Waiting 15 seconds for grades in {TOPICO_NOTAS}...")
    try:
        cliente.loop_start()
        time.sleep(15)
        cliente.loop_stop()
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user.")
    finally:
        print("[*] Closing grades check.")
        cliente.disconnect()


if __name__ == "__main__":
    main()
