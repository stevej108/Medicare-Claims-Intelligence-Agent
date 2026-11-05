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


def test_groq_requires_api_key(
    monkeypatch,
):
    monkeypatch.setattr(
        "core.llm.LLM_PROVIDER",
        "groq",
    )

    monkeypatch.setattr(
        "core.llm.GROQ_API_KEY",
        None,
    )

    with pytest.raises(
        ValueError,
        match="GROQ_API_KEY is required",
    ):
        get_llm()

def test_groq_requires_model(
    monkeypatch,
):
    monkeypatch.setattr(
        "core.llm.LLM_PROVIDER",
        "groq",
    )

    monkeypatch.setattr(
        "core.llm.GROQ_API_KEY",
        "fake-test-key",
    )

    monkeypatch.setattr(
        "core.llm.GROQ_MODEL",
        "",
    )

    with pytest.raises(
        ValueError,
        match="GROQ_MODEL is required",
    ):
        get_llm()
        
                        