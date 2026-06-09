import logging
from uts_key_manager import escanear_e_salvar_chaves, listar_chaves_confiadas
from config import ID_UNIDADE, ORACULO_RSA_PUB_B64, ORACULO_ECDSA_PUB_B64
from keys import carregar_ou_gerar_chaves, load_rsa_pub_key, load_ecdsa_pub_key
from identity import publicar_identidade
from challenge import solicitar_desafio
from decrypt import decifrar_mensagem
from encrypt import cifrar_mensagem
from respond import enviar_resposta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(ID_UNIDADE)


def main():
    # Carregar chaves
    chaves = carregar_ou_gerar_chaves()
    oraculo_rsa_pub = load_rsa_pub_key(ORACULO_RSA_PUB_B64)
    oraculo_ecdsa_pub = load_ecdsa_pub_key(ORACULO_ECDSA_PUB_B64)
    log.info("✅ Chaves carregadas")

    # Publicar identidade e escanear rede
    publicar_identidade({
        "id_unidade":          ID_UNIDADE,
        "chave_publica_rsa":   chaves["rsa"]["public_key"],
        "chave_publica_ecdsa": chaves["ecdsa"]["public_key"]
    })
    escanear_e_salvar_chaves()
    listar_chaves_confiadas()

    # Solicitar e decifrar desafio
    mensagem_oraculo = solicitar_desafio()
    if not mensagem_oraculo:
        log.warning("⚠️ Nenhuma resposta recebida — tente rodar novamente")
        return

    pergunta = decifrar_mensagem(mensagem_oraculo, oraculo_ecdsa_pub)
    if not pergunta:
        log.error("❌ Falha ao decifrar a pergunta do Oráculo")
        return

    print(f"\n❓ {pergunta}")

    # Ler resposta e enviar
    resposta = input("✏️  Resposta: ").strip()
    if not resposta:
        log.warning("⚠️ Nenhuma resposta fornecida")
        return

    pacote = cifrar_mensagem(resposta, oraculo_rsa_pub)
    if pacote:
        enviar_resposta(pacote)
    else:
        log.error("❌ Falha ao cifrar a resposta")


if __name__ == "__main__":
    main()
