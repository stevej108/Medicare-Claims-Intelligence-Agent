import logging

from fastapi import FastAPI, HTTPException

from agents.run import run_claims_agent
from src.api.schemas import QueryRequest, QueryResponse


logger = logging.getLogger(__name__)


app = FastAPI(
    title="Medicare Claims Intelligence API",
    description="API for the Medicare Claims Intelligence Agent.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query_agent(request: QueryRequest):
    try:
        result = run_claims_agent(
            request.question
        )

        return QueryResponse(
            answer=result["answer"]
        )

    except Exception as exc:
        logger.exception(
            "Claims agent failed to process request."
        )

        raise HTTPException(
            status_code=500,
            detail="Claims agent failed to process the request.",
        ) from exc