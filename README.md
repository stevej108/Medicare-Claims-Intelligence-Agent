# Medicare Claims Intelligence Agent

## Overview

The **Medicare Claims Intelligence Agent** is an end-to-end AI engineering project for exploring synthetic Medicare claims analytics through natural-language questions.

The system combines deterministic healthcare analytics with agentic AI while deliberately separating **numerical computation from language-model reasoning**.

> **LLMs reason. Deterministic tools calculate. RAG grounds methodology. LangGraph orchestrates evidence.**

Rather than allowing an LLM to generate arbitrary SQL or calculate healthcare metrics directly, the agent routes analytical questions to a controlled set of validated DuckDB-backed tools operating on a canonical Medicare beneficiary-year semantic layer.

The project has evolved beyond the analytical agent itself into a deployable AI service demonstrating:

- FastAPI API development
- Pydantic request and response contracts
- Docker containerization
- provider-independent LLM configuration
- local and hosted LLM inference
- resource-aware model loading
- mocked API testing
- deterministic, data-integration, and LLM-integration test layers
- automated GitHub Actions CI
- CI-gated continuous deployment
- cloud deployment on Render
- environment-based configuration and secrets management

The deployed API uses **Groq-hosted Qwen inference**, while local development can continue using **Qwen through Ollama**.

---

## Live Application

The deployed FastAPI service is available at:

**https://medicare-claims-intelligence-agent.onrender.com**

Interactive API documentation:

**https://medicare-claims-intelligence-agent.onrender.com/docs**

Health endpoint:

**https://medicare-claims-intelligence-agent.onrender.com/health**

The deployment runs as a Dockerized FastAPI service on Render. Successful commits to `main` must pass the GitHub Actions CI pipeline before the deployment workflow is allowed to trigger Render.

---

## Project Motivation

This project builds on the analytical foundation developed in the companion **CMS Medicare Utilization Analytics** project.

That work transforms CMS DE-SynPUF claims into a validated longitudinal beneficiary-year analytical layer covering:

- healthcare utilization
- annual healthcare costs
- cost concentration
- chronic-condition burden
- longitudinal high-cost persistence
- payer-oriented member segmentation

The Claims Intelligence Agent asks a different question:

> **How can AI make trusted healthcare analytics accessible through natural language without allowing the language model to become the source of truth for numerical calculations?**

The result is a hybrid architecture where:

- DuckDB owns calculations
- controlled Python tools own analytical capabilities
- RAG owns methodological knowledge
- LLMs interpret and synthesize
- LangGraph coordinates the workflow
- FastAPI exposes the application as a service

---

## System Architecture

```text
                         User / API Client
                                │
                                ▼
                             FastAPI
                                │
                         Pydantic Validation
                                │
                                ▼
                       Claims Intelligence Agent
                                │
                                ▼
                        LangGraph Planner
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
            Analytics        Knowledge        Hybrid
                │               │               │
                ▼               ▼          ┌────┴────┐
           LLM Router          FAISS        ▼         ▼
                │               │       Analytics    RAG
                ▼               │           │         │
        Canonical ToolRoute     │           ▼         │
                │               │        DuckDB       │
                ▼               │           │         │
            Dispatcher          │           └────┬────┘
                │               │                │
                ▼               │                ▼
         Validated Tools        │         Hybrid Synthesis
                │               │                │
                ▼               │                │
             DuckDB             │                │
                └───────────────┴────────────────┘
                                │
                                ▼
                          LLM Synthesis
                                │
                                ▼
                      Grounded API Response
```

---

## AI Engineering Architecture

The application supports different inference environments without changing the agent implementation.

```text
                    get_llm()
                       │
                 LLM_PROVIDER
                 ┌─────┴─────┐
                 │           │
                 ▼           ▼
              Ollama        Groq
                 │           │
             qwen3:8b   Hosted Qwen
                 │           │
                 ▼           ▼
          Local Development   Cloud Deployment
```

Configuration is supplied through environment variables rather than hard-coded deployment assumptions.

Example local configuration:

```text
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

Cloud configuration:

```text
LLM_PROVIDER=groq
GROQ_MODEL=qwen/qwen3.8-27b
GROQ_API_KEY=<secret>
```

Secrets are never committed to source control.

---

## API Layer

FastAPI exposes the agent through a programmatic service interface.

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

This endpoint is used both by the hosting platform and by automated container smoke tests.

### Claims Query

```http
POST /query
```

Example request:

```json
{
  "question": "Describe the pharmacy-intensive chronic population."
}
```

The API:

1. validates the request with Pydantic
2. invokes the Claims Intelligence Agent
3. executes validated analytical or retrieval tools
4. synthesizes the grounded response
5. returns a controlled response contract

The API intentionally does not expose the internal LangGraph state directly.

This separates the public application interface from the implementation details of the agent.

---

## Design Principles

### 1. Deterministic Analytics

Numerical healthcare analytics are calculated by tested DuckDB-backed Python tools.

The LLM does not calculate:

- utilization rates
- cost concentration
- segment profiles
- chronic-condition prevalence
- population statistics

Instead, it identifies the required analytical capability and passes validated arguments to deterministic tools.

---

### 2. Controlled Tool Use

The analytical layer exposes a constrained set of capabilities.

#### Population Analytics

```python
get_population_summary()
```

Returns population size, annual cost measures, and healthcare utilization statistics.

#### Segment Profiling

```python
get_segment_profile(segment)
```

Returns utilization, cost, and clinical characteristics for one canonical member segment.

#### Segment Comparison

```python
compare_segments(segment_a, segment_b)
```

Compares two segments across shared cost, utilization, and chronic-condition measures.

#### Cost Concentration

```python
get_cost_concentration(top_fraction)
```

Measures the proportion of positive healthcare spending attributable to selected highest-cost portions of the population.

#### Chronic-Condition Prevalence

```python
get_condition_prevalence(segment)
```

Returns ranked chronic-condition prevalence for a validated segment.

---

### 3. Stable API Contracts

FastAPI and Pydantic establish a boundary between external API consumers and the internal AI system.

```text
HTTP JSON
    ↓
QueryRequest
    ↓
Agent Internals
    ↓
QueryResponse
    ↓
HTTP JSON
```

Internal routing state, DuckDB results, and orchestration structures can evolve without requiring the public API contract to change.

---

### 4. Externalized Configuration

Infrastructure-specific configuration is provided through environment variables.

The code does not assume:

- a specific LLM provider
- a specific Ollama host
- a particular deployment machine
- locally stored secrets

This allows the same application to operate with local Ollama inference during development and hosted Groq inference after deployment.

---

## DuckDB Semantic Layer

The application reads validated analytical data directly from Parquet.

```text
member_year.parquet
        │
        ├─────────────────┐
        │                 │
        ▼                 ▼
  Member-Year Data   High-Cost Persistence
        │                 │
        └────────┬────────┘
                 ▼
       analytical_member_year
                 │
                 ▼
          Analytical Tools
```

The semantic layer defines shared business logic once so individual tools do not independently recreate analytical definitions.

### Composite Annual Cost

```text
total_annual_cost =
    MEDREIMB_IP
  + MEDREIMB_OP
  + MEDREIMB_CAR
  + rx_total_cost
```

### Chronic-Condition Burden

Eleven CMS chronic-condition indicators are converted into a beneficiary-year chronic-condition count.

### Inpatient Utilization

```text
has_inpatient_utilization =
    inpatient_claims > 0
```

### Member Segmentation

Six mutually exclusive analytical segments are generated deterministically:

1. Persistent high-cost complex
2. Recurrent high-cost complex
3. Acute episodic high cost
4. Pharmacy-intensive chronic
5. High routine utilization
6. Stable / lower utilization

The segmentation combines utilization patterns, chronic-condition burden, longitudinal high-cost persistence, and population-relative percentile thresholds.

---

## Retrieval-Augmented Generation

Structured claims analytics and methodological knowledge are intentionally separated.

RAG handles questions such as:

- How is total annual cost calculated?
- What does MEDREIMB_IP mean?
- How is persistent high-cost complex defined?
- How was the member-year dataset constructed?
- What are the limitations of DE-SynPUF?
- Can findings be generalized to actual Medicare beneficiaries?

The knowledge corpus includes:

```text
knowledge/
├── analytical_methodology.md
├── cohort_definitions.md
├── limitations.md
└── metric_definitions.md
```

The retrieval pipeline is:

```text
Knowledge Documents
        ↓
Semantic Chunking
        ↓
Sentence Transformers
        ↓
Vector Embeddings
        ↓
FAISS
        ↓
Relevant Passages
        ↓
LLM Synthesis
```

Retrieved passages retain source provenance.

### Resource-Aware Loading

Sentence Transformers is imported lazily rather than during application startup.

This reduces baseline memory consumption and prevents the embedding stack, including Transformers and PyTorch dependencies, from being initialized when the application only needs lightweight endpoints such as `/health`.

This became particularly important when deploying the service into a memory-constrained container environment.

---

## LangGraph Workflow

LangGraph coordinates three execution modes.

### Analytics Mode

```text
Question
   ↓
Planner
   ↓
Analytics
   ↓
LLM Tool Router
   ↓
Canonical ToolRoute
   ↓
Dispatcher
   ↓
DuckDB
   ↓
Validated Result
   ↓
LLM Synthesis
```

### Knowledge Mode

```text
Question
   ↓
Planner
   ↓
Knowledge
   ↓
FAISS Retrieval
   ↓
Relevant Documentation
   ↓
LLM Synthesis
```

### Hybrid Mode

Hybrid questions require both analytical evidence and methodological context.

Example:

> Compare persistent high-cost complex members with pharmacy-intensive chronic members, explain how each cohort is defined, and summarize the main utilization differences.

```text
                    Question
                       │
                    Planner
                       │
              ┌────────┴────────┐
              ▼                 ▼
       Analytical Need     Knowledge Need
              │                 │
              ▼                 ▼
       compare_segments       FAISS RAG
              │                 │
              ▼                 ▼
            DuckDB       Cohort Definitions
              │                 │
              └────────┬────────┘
                       ▼
                Hybrid Synthesis
                       │
                       ▼
                Grounded Answer
```

---

## Controlled Routing

The application combines deterministic routing logic with LLM-assisted routing.

High-confidence intents can bypass probabilistic model selection.

Examples include:

- metric definitions
- methodology
- limitations
- population-generalization questions

Analytical requests are routed to validated tools.

More ambiguous analyst questions can be resolved using structured Pydantic outputs from the configured LLM.

Model-generated segment names are normalized against a canonical controlled vocabulary before execution.

For example:

```text
Acute episodic high-cost
```

and:

```text
Acute episodic high cost
```

can resolve to the same approved analytical segment.

---

## Testing Strategy

The test suite is intentionally separated by infrastructure dependency.

### Portable Tests

Portable tests require neither local analytical data nor a live LLM service.

They cover:

- Pydantic models
- validation
- canonicalization
- isolated routing logic
- API contracts
- mocked Claims Agent behavior
- API error handling
- LLM-provider configuration

Run with:

```powershell
pytest -m "not llm and not data" -v
```

These tests form the primary automated CI gate.

---

### Data Integration Tests

Data tests execute against the validated processed DE-SynPUF analytical artifacts.

They cover:

- population statistics
- cost concentration
- segment profiles
- condition prevalence
- analytical dispatch
- DuckDB semantic-layer behavior

Run with:

```powershell
pytest -m data -v
```

Known results from the upstream CMS Medicare Utilization Analytics project provide regression targets.

---

### LLM Integration Tests

LLM-marked tests exercise model-dependent behavior using a live configured provider.

They evaluate areas such as:

- natural-language routing
- ambiguous intent resolution
- model-generated analytical arguments

Run with:

```powershell
pytest -m llm -v
```

Keeping these tests separate prevents model latency or inference availability from making portable CI unstable.

---

## API Testing and Mocking

FastAPI endpoint tests use `TestClient`.

The Claims Agent is mocked where appropriate so API tests can verify:

- HTTP status codes
- request validation
- response schemas
- agent invocation
- failure behavior

without invoking an actual LLM on every test.

This establishes a separation between:

```text
API contract testing
```

and:

```text
AI integration testing
```

Internal exceptions are logged server-side while callers receive controlled HTTP error responses.

---

## Containerization

The API is packaged as a Docker image.

The container:

1. starts from a slim Python base
2. installs pinned runtime dependencies
3. copies application code and required synthetic analytical artifacts
4. starts Uvicorn
5. exposes the FastAPI service

The containerized application binds on:

```text
0.0.0.0
```

so it can receive traffic from the host/container runtime.

The project also uses `.dockerignore` to keep unnecessary development artifacts out of the Docker build context.

---

## CI/CD Pipeline

GitHub Actions implements automated continuous integration and gated deployment.

```text
                       Push to main
                            │
                            ▼
                     GitHub Actions
                            │
                            ▼
                    Portable pytest
                            │
                          PASS
                            │
                            ▼
                    Build Docker Image
                            │
                          PASS
                            │
                            ▼
                    Start Container
                            │
                            ▼
                       GET /health
                            │
                          200 OK
                            │
                            ▼
                      CI Successful
                            │
                            ▼
                     deploy.yml
                            │
                            ▼
                  Render Deploy Hook
                            │
                            ▼
                     Render Deployment
                            │
                            ▼
                     FastAPI Service
```

A failed CI workflow prevents the deployment workflow from triggering.

Deployment occurs only after the application:

- passes the portable test suite
- builds successfully as a Docker image
- starts successfully as a container
- responds successfully to the `/health` smoke test

Render's direct Auto-Deploy behavior is disabled so GitHub Actions remains the deployment gate.

---

## Cloud Deployment

The application is deployed as a Dockerized Web Service on Render.

The hosted environment uses:

```text
LLM_PROVIDER=groq
```

with the Groq API credential supplied as a deployment secret.

Local development retains:

```text
LLM_PROVIDER=ollama
```

This means cloud deployment does not require changing application logic.

The deployment surfaced and resolved several practical engineering constraints, including:

- Linux-versus-local environment differences
- application/data artifact separation
- secret management
- memory-constrained container startup
- lazy loading of ML dependencies
- health-check design
- external LLM configuration
- CI-gated deployment

---

## Local Development vs. Cloud Deployment

| Capability | Local | Cloud |
|---|---|---|
| API | FastAPI | FastAPI |
| Analytics | DuckDB | DuckDB |
| Data | Synthetic DE-SynPUF Parquet | Synthetic DE-SynPUF Parquet |
| Orchestration | LangGraph | LangGraph |
| LLM | Ollama / Qwen3:8B | Groq / Qwen |
| RAG | FAISS + Sentence Transformers | FAISS + Sentence Transformers |
| UI | Streamlit | FastAPI `/docs` |
| Container | Optional | Docker |
| CI | GitHub Actions | GitHub Actions |
| CD | N/A | GitHub Actions → Render |

---

## Streamlit Interface

The repository also includes a lightweight local Streamlit interface for interactive analyst exploration.

Example questions include:

### Population

> What percentage of member-years had inpatient utilization?

### Segment Analysis

> Describe the pharmacy-intensive chronic population.

### Cost Concentration

> What share of positive healthcare spending comes from the top 10% of member-years?

### Knowledge Retrieval

> How is total annual cost calculated?

### Hybrid Analysis

> Compare persistent high-cost complex members with pharmacy-intensive chronic members, explain how each cohort is defined, and summarize the main utilization differences.

The local interface can expose additional execution metadata useful during development, including routing mode, selected tools, arguments, and retrieved knowledge sources.

---

## Repository Structure

```text
medicare-claims-intelligence-agent/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── agents/
│   ├── dispatcher.py
│   ├── hybrid_synthesizer.py
│   ├── planner.py
│   ├── reporting.py
│   ├── router.py
│   ├── run.py
│   ├── state.py
│   ├── synthesizer.py
│   └── workflow.py
│
├── core/
│   ├── llm.py
│   └── models.py
│
├── data/
│   └── processed/
│       ├── high_cost_persistence.parquet
│       └── member_year.parquet
│
├── database/
│   ├── connection.py
│   └── schema.py
│
├── knowledge/
│   ├── analytical_methodology.md
│   ├── cohort_definitions.md
│   ├── limitations.md
│   └── metric_definitions.md
│
├── prompts/
│   ├── hybrid_synthesis.py
│   ├── planner.py
│   ├── synthesis.py
│   └── tool_router.py
│
├── rag/
│   ├── documents.py
│   ├── embeddings.py
│   └── retriever.py
│
├── src/
│   └── api/
│       ├── __init__.py
│       ├── app.py
│       └── schemas.py
│
├── tests/
│   ├── test_api.py
│   ├── test_condition.py
│   ├── test_costs.py
│   ├── test_dispatcher.py
│   ├── test_llm.py
│   ├── test_models.py
│   ├── test_population.py
│   ├── test_routing.py
│   └── test_segments.py
│
├── tools/
│   ├── conditions.py
│   ├── costs.py
│   ├── knowledge.py
│   ├── population.py
│   └── segments.py
│
├── ui/
│   └── app.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## Technology Stack

### Data and Analytics

- Python
- DuckDB
- Parquet
- Pydantic
- CMS DE-SynPUF-derived synthetic analytical data

### Agentic AI

- LangGraph
- LangChain
- Qwen
- Ollama
- Groq

### Retrieval-Augmented Generation

- Sentence Transformers
- FAISS
- semantic Markdown chunking

### API and Application

- FastAPI
- Uvicorn
- Streamlit
- OpenAPI / Swagger

### Engineering and Delivery

- Docker
- GitHub Actions
- CI/CD
- Render
- environment-based configuration
- secrets management
- health-check smoke testing

### Testing

- pytest
- FastAPI TestClient
- mocking
- deterministic regression testing
- data integration testing
- LLM integration testing

---

## Data and Reproducibility

The project uses analytical artifacts derived from the **CMS Data Entrepreneurs' Synthetic Public Use File (DE-SynPUF)**.

The upstream CMS Medicare Utilization Analytics project performs the claims engineering and construction of the beneficiary-year analytical layer.

This repository intentionally consumes that validated layer rather than rebuilding the raw claims pipeline:

```text
CMS Synthetic Claims
        ↓
Claims Engineering
        ↓
Validated Semantic Data Product
        ↓
Claims Intelligence Agent
```

Two processed synthetic Parquet artifacts are included in this repository to make the deployed analytical service reproducible:

```text
data/processed/member_year.parquet
data/processed/high_cost_persistence.parquet
```

These contain synthetic analytical data and are included specifically to support the portfolio deployment.

---

## Engineering Decisions

### Why DuckDB?

The analytical workload is structured, deterministic, and naturally operates over Parquet. DuckDB allows analytical tools to query the data directly without introducing a separate database server into the portfolio deployment.

### Why Not LLM-Generated SQL?

The application is designed around trusted analytical tools rather than arbitrary generated queries.

This improves:

- validation
- reproducibility
- testability
- business-rule consistency
- analytical traceability

### Why Multiple LLM Providers?

Local development and cloud deployment have different infrastructure constraints.

Provider abstraction allows:

```text
Local → Ollama
Cloud → Groq
```

while keeping orchestration, prompts, retrieval, and analytical logic unchanged.

### Why Lazy-Load Sentence Transformers?

The initial cloud deployment exceeded the memory available during application startup.

Moving the Sentence Transformers import to the retrieval execution path allowed lightweight API endpoints to start without eagerly loading the full embedding and Transformer stack.

This reduced startup memory requirements without removing RAG capability.

### Why Separate Test Categories?

Not every valid test has the same infrastructure requirements.

The project distinguishes:

- portable tests
- analytical-data integration tests
- LLM integration tests

This keeps CI deterministic while preserving broader end-to-end validation locally.

### Why CI-Gated Deployment?

Render Auto-Deploy is intentionally disabled.

GitHub Actions triggers the deployment only after tests, Docker image creation, container startup, and the health smoke test succeed.

This prevents a failed CI build from automatically becoming the deployed application.

---

## Limitations

This project is a portfolio demonstration using synthetic Medicare-style data.

It should not be interpreted as:

- a clinical decision-support system
- a validated care-management system
- an actuarial Medicare model
- an eligibility or coverage engine
- a utilization-management application

DE-SynPUF does not represent actual Medicare beneficiaries.

The analytical segments are transparent constructs developed from patterns in the synthetic dataset and would require independent validation before use with another population.

LLMs can still make interpretation, routing, or synthesis errors. The architecture therefore keeps numerical calculations outside the LLM and exposes controlled analytical capabilities.

Free-tier cloud infrastructure also introduces operational limitations such as cold starts, resource constraints, and hosted-model rate limits.

---

## Project Objective

The Medicare Claims Intelligence Agent demonstrates a practical approach to building AI systems around trusted analytics:

> **LLMs reason. Deterministic tools calculate. RAG grounds methodology. LangGraph orchestrates evidence. APIs expose capabilities. Containers make them portable. CI/CD makes them deployable.**

The project is intentionally designed not just as an AI demonstration, but as an **end-to-end AI engineering system** spanning analytical architecture, agent orchestration, API development, testing, containerization, configuration management, hosted inference, and automated deployment.