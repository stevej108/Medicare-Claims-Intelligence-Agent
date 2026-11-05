import pytest

from core.llm import get_llm


def test_default_llm_provider():
    llm = get_llm()

    assert llm.model == "qwen3:8b"

def test_unsupported_llm_provider(monkeypatch):
    monkeypatch.setattr(
        "core.llm.LLM_PROVIDER",
        "unsupported",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported LLM provider",
    ):
        get_llm()    