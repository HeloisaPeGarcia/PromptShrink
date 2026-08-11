"""
Testes para compressão de histórico de chat (chat_compressor.py)
"""

from promptshrink.chat_compressor import compress_chat_history


def test_compress_chat_history():
    messages = [
        {"role": "user", "content": "Olá! Eu gostaria que você pudesse, por favor, me responder algo."},
        {"role": "assistant", "content": "Certamente, como posso te ajudar?"},
        {"role": "user", "content": "Explique a teoria da relatividade concisamente."},
    ]

    res = compress_chat_history(messages, model="gpt-4o", keep_last_n=1)
    assert len(res["messages"]) == 3
    assert res["tokens_saved"] > 0
    # A última mensagem do usuário foi preservada intacta
    assert res["messages"][-1]["content"] == messages[-1]["content"]
    # A primeira mensagem foi comprimida
    assert "por favor" not in res["messages"][0]["content"]
