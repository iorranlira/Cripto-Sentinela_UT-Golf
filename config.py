
ID_UNIDADE = "ut-golf"
BROKER = "broker.hivemq.com"
PORT   = 1883

TOPICO_BROADCAST_CHAVES = f"sisdef/broadcast/chaves/{ID_UNIDADE}"
TOPICO_ORACULO          = "sisdef/direto/oraculo"
TOPICO_RESPOSTA         = f"sisdef/direto/{ID_UNIDADE}"
TOPICO_REVOGACAO        = "sisdef/broadcast/revogacao"

ORACULO_RSA_PUB_B64   = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0JYEsxupPYOio+u8xHdzSNLQgQoPwFx/qceHQJPy2KzNSCXz3FFyKkXaso4UTorzy8XXDv5WkRC1AlDDVu28ANXlrZqLyjLZ8DdplHig2KSxYV5MXA5TyqMDeCAW5CWi+na5Xwr9IbtuTfCv65YeB3QRgZWjZ4oVxpGVek+4dec0qChNl6pL9KmgI4u5CHHC8d7z6MovK0+eN0aMIT2bWgri29tT9sDCoHEGaab1576+SXK3iDXlLkeehJ/h72lqu3HmSL/B5ZE+pKLVLJogSwwMCTejrfTXf5acj9EOq83wGNLTjHIKr2iMz+SZzFS4vxk6qMgltCXjBZfXalzLnwIDAQAB"
ORACULO_ECDSA_PUB_B64 = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEfmgdDET1IKOR2OxLI9KBBzFB97GyrJKipAuwSrMhDn1w93ieoCb7etbYX5/wrUic9xX5LQbUdgyKSRuCnTPAeQ=="


ARQUIVO_CHAVES = "chaves_confiadas.json"

CAMPOS_OBRIGATORIOS = [
    "ciphertext_b64",
    "tag_autenticacao_b64",
    "nonce_b64",
    "chave_sessao_cifrada_b64",
    "assinatura_b64"
]