from fastapi.testclient import TestClient

from src.api.app import app


client = TestClient(app)


def test_health_check_returns_200():
    response = client.get("/health")

    assert response.status_code == 200


def test_health_check_returns_expected_response():
    response = client.get("/health")

    assert response.json() == {"status": "ok"}


from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.app import app


client = TestClient(app)


def test_query_returns_agent_answer():
    mock_result = {
        "question": "Describe the pharmacy-intensive chronic population.",
        "answer": "Mock claims agent response.",
        "tool": "get_segment_profile",
        "arguments": {
            "segment": "Pharmacy-intensive chronic"
        },
        "tool_result": {},
        "sources": [],
        "data_context": "CMS DE-SynPUF synthetic Medicare data",
        "synthetic_data_notice": "Synthetic data.",
    }

    with patch(
        "src.api.app.run_claims_agent",
        return_value=mock_result,
    ) as mock_agent:

        response = client.post(
            "/query",
            json={
                "question": (
                    "Describe the pharmacy-intensive "
                    "chronic population."
                )
            },
        )

    assert response.status_code == 200

    assert response.json() == {
        "answer": "Mock claims agent response."
    }

    mock_agent.assert_called_once_with(
        "Describe the pharmacy-intensive chronic population."
    )    

def test_query_rejects_missing_question():
    response = client.post(
        "/query",
        json={},
    )

    assert response.status_code == 422    


def test_query_handles_agent_failure():
    with patch(
        "src.api.app.run_claims_agent",
        side_effect=RuntimeError("LLM connection failed"),
    ):
        response = client.post(
            "/query",
            json={
                "question": "Describe the pharmacy-intensive chronic population."
            },
        )

    assert response.status_code == 500

    assert response.json() == {
        "detail": "Claims agent failed to process the request."
    }    