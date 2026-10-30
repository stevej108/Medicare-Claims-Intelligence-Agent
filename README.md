# Medicare Claims Intelligence Agent

## Overview

The Medicare Claims Intelligence Agent is a locally hosted agentic AI application for exploring synthetic Medicare claims analytics using natural-language questions.

The project combines:

- validated CMS DE-SynPUF analytical data
- DuckDB for deterministic claims analytics
- Qwen3:8B running locally through Ollama
- retrieval-augmented generation (RAG)
- FAISS semantic search
- Sentence Transformers embeddings
- LangGraph orchestration
- Pydantic validation
- Streamlit
- automated unit and routing tests

The core design principle is simple:

**The language model reasons about the question. Deterministic analytical tools calculate the answer.**

Rather than allowing an LLM to generate arbitrary SQL or Python, the agent routes analytical questions to a controlled set of tested tools built on top of a validated Medicare beneficiary-year semantic layer.

Documentation, methodology, cohort definitions, and limitations are handled separately through retrieval-augmented generation.

This separation allows the system to distinguish between questions such as:

> **What percentage of beneficiary-years had inpatient utilization?**

and:

> **How is total annual cost defined?**

The first requires structured analytical computation.

The second requires methodological knowledge retrieval.

Hybrid questions can use both.

---

## Project Motivation

This project builds on the analytical foundation developed in the companion repository:

**CMS Medicare Utilization Analytics**

That project transformed CMS DE-SynPUF claims into a validated longitudinal beneficiary-year analytical layer and explored:

- healthcare utilization
- cost concentration
- chronic-condition burden
- longitudinal high-cost persistence
- payer-oriented member segmentation

The Claims Intelligence Agent uses those validated analytical outputs as its semantic data foundation.

The objective of this second project is different:

> **How can agentic AI make trusted healthcare analytics accessible through natural language without allowing the language model to become the source of truth for numerical calculations?**

---

## Architecture

```text
                         User Question
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
         Qwen Router         FAISS        ▼         ▼
              │               │        Analytics   RAG
              ▼               │           │         │
       Canonical ToolRoute    │           ▼         │
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
                           Qwen3:8B
                              │
                              ▼
                    Grounded Analyst Answer
                              │
                              ▼
                          Streamlit
```

---

## Design Principles

### 1. Deterministic Analytics

Numerical healthcare analytics are calculated by DuckDB-backed Python tools.

The language model does not calculate:

- utilization rates
- cost concentration
- segment profiles
- chronic-condition prevalence
- population statistics

Instead, the model selects an appropriate validated analytical capability.

---

### 2. Controlled Tool Use

The analytical layer exposes a limited set of tested capabilities:

#### Population Analytics

`get_population_summary()`

Returns high-level member-year statistics including population size, annual cost measures, and utilization prevalence.

#### Segment Profiling

`get_segment_profile(segment)`

Returns utilization, cost, and clinical characteristics for one validated member segment.

#### Segment Comparison

`compare_segments(segment_a, segment_b)`

Compares two member segments across canonical utilization, cost, and chronic-condition measures.

#### Cost Concentration

`get_cost_concentration(top_fraction)`

Measures the proportion of positive healthcare spending attributable to selected highest-cost portions of the beneficiary-year population.

#### Chronic-Condition Prevalence

`get_condition_prevalence(segment)`

Returns ranked chronic-condition prevalence within a validated member segment.

All analytical tools operate against a shared DuckDB semantic layer.

---

## DuckDB Semantic Layer

The application reads the processed Medicare analytical data directly from Parquet.

```text
member_year.parquet
        │
        ├───────────────┐
        │               │
        ▼               ▼
member_year        high_cost_persistence
        │               │
        └───────┬───────┘
                ▼
      analytical_member_year
```

The semantic layer defines canonical derived measures once so individual tools do not independently recreate business logic.

Examples include:

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

The semantic layer deterministically reproduces six mutually exclusive analytical segments originally developed in the CMS Medicare Utilization Analytics project:

1. Persistent high-cost complex
2. Recurrent high-cost complex
3. Acute episodic high cost
4. Pharmacy-intensive chronic
5. High routine utilization
6. Stable / lower utilization

---

## Local Language Model

The project uses:

```text
Qwen3:8B
```

running locally through:

```text
Ollama
```

with the LangChain Ollama integration.

Example configuration:

```python
llm = ChatOllama(
    model="qwen3:8b",
    temperature=0.2,
)
```

The local model is responsible for:

- question interpretation
- analytical tool selection
- hybrid-question planning
- answer synthesis

It is not responsible for numerical healthcare calculations.

---

## Retrieval-Augmented Generation

Structured claims analytics and methodological knowledge are intentionally separated.

RAG is used for questions such as:

- How is total annual cost calculated?
- What does MEDREIMB_IP mean?
- How is Persistent High-Cost Complex defined?
- How was the member-year analytical dataset constructed?
- What are the limitations of DE-SynPUF?
- Can findings from this project be generalized to actual Medicare populations?

The initial knowledge corpus includes:

```text
knowledge/
├── analytical_methodology.md
├── cohort_definitions.md
├── limitations.md
└── metric_definitions.md
```

Markdown documents are divided into heading-based semantic chunks.

Embeddings are generated locally using Sentence Transformers and indexed using FAISS.

```text
Knowledge Documents
        ↓
Semantic Chunking
        ↓
Sentence Transformer
        ↓
Vector Embeddings
        ↓
FAISS
        ↓
Relevant Knowledge Passages
        ↓
Qwen Synthesis
```

Retrieved results retain document-level provenance so the application can display supporting knowledge sources.

---

## LangGraph Agent Workflow

LangGraph coordinates three analytical modes.

### Analytics Mode

Used when the question requires numerical evidence.

```text
Question
   ↓
Planner
   ↓
Analytics
   ↓
Qwen Tool Router
   ↓
Canonical ToolRoute
   ↓
Dispatcher
   ↓
DuckDB
   ↓
Validated Result
   ↓
Qwen Synthesis
```

---

### Knowledge Mode

Used for methodology, definitions, provenance, and limitations.

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
Qwen Synthesis
```

---

### Hybrid Mode

Used when a question requires both analytical results and methodological context.

Example:

> Compare persistent high-cost complex members with pharmacy-intensive chronic members, explain how each cohort is defined, and summarize the main utilization differences.

The graph decomposes the request into:

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
       compare_segments      FAISS RAG
              │                 │
              ▼                 ▼
            DuckDB        Cohort Definitions
              │                 │
              └────────┬────────┘
                       ▼
                Hybrid Synthesis
                       │
                       ▼
                Grounded Answer
```

This hybrid workflow represents the primary agentic capability of the project.

---

## Controlled Routing

The application combines deterministic routing rules with local-LLM routing.

High-confidence intents such as explicit requests for:

- metric definitions
- methodology
- limitations
- population generalization

can be routed directly to the knowledge retriever.

Clear analytical requests are routed to validated analytical tools.

Ambiguous analyst questions are resolved by Qwen using structured Pydantic output.

Model-generated segment names are normalized to a canonical controlled vocabulary before tool execution.

This prevents small differences such as:

```text
Acute episodic high-cost
```

and:

```text
Acute episodic high cost
```

from breaking analytical execution.

---

## Validation and Testing

A major focus of the project is preventing probabilistic model behavior from changing deterministic analytical results.

The test suite covers:

### Analytical Validation

Known results from the CMS Medicare Utilization Analytics project are used as regression targets.

Examples include:

- total beneficiary-year population
- healthcare utilization prevalence
- member-segment profiles
- healthcare spending concentration
- chronic-condition prevalence structure

### Input Validation

Pydantic and Enum-based models constrain:

- analytical tool names
- member segment names
- cost-concentration inputs
- router outputs

### Routing Evaluation

Natural-language analyst questions are evaluated against expected tool selections and arguments.

### Canonicalization Testing

Model-generated variations of member-segment names are mapped to approved analytical values.

### RAG Testing

Retrieval tests verify that questions about:

- metric definitions
- cohort definitions
- methodology
- analytical limitations

surface the appropriate knowledge documents.

Tests are separated into deterministic and local-model suites.

```powershell
python -m pytest -m "not llm" -v
```

runs deterministic tests.

```powershell
python -m pytest -m "llm" -v
```

evaluates local-model routing behavior.

---

## Streamlit Interface

The application provides a lightweight analyst-facing interface.

Users can ask questions such as:

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

Responses include:

- grounded analyst-facing explanation
- execution mode
- analytical tool used
- tool arguments
- retrieved knowledge sources
- synthetic-data disclaimer

The execution trace makes the agent's reasoning path visible instead of presenting the application as a black-box chatbot.

---

## Repository Structure

```text
medicare-claims-intelligence-agent/
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
│   ├── config.py
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
├── notebooks/
│   ├── 01_duckdb_exploration.ipynb
│   ├── 02_llm_routing.ipynb
│   └── 03_rag_retrieval.ipynb
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
├── tests/
│   ├── test_conditions.py
│   ├── test_costs.py
│   ├── test_dispatcher.py
│   ├── test_population.py
│   ├── test_router.py
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
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

Adjust that tree to match the final files you actually have before publishing.

---

## Technology Stack

### Data and Analytics

- Python
- DuckDB
- pandas
- PyArrow
- Parquet
- Pydantic

### Agentic AI

- Qwen3:8B
- Ollama
- LangChain Ollama
- LangGraph

### Retrieval-Augmented Generation

- Sentence Transformers
- FAISS
- heading-aware Markdown chunking

### Application

- Streamlit

### Testing

- pytest
- deterministic regression testing
- local-LLM routing evaluation

---

## Data Source

This project uses analytical outputs derived from the CMS Data Entrepreneurs' Synthetic Public Use File (DE-SynPUF).

The upstream companion project performs the claims engineering and member-year construction:

**CMS Medicare Utilization Analytics**

The agent project intentionally consumes the validated analytical layer rather than rebuilding raw claims transformations.

This separation mirrors a common analytical architecture:

```text
Claims Pipeline
      ↓
Validated Semantic Data Product
      ↓
Analytics / AI Consumption Layer
```

---

## Limitations

This project is a portfolio demonstration using synthetic Medicare-style data.

The application should not be interpreted as:

- a clinical decision-support system
- a validated care-management system
- an actuarial Medicare cost model
- an eligibility or coverage engine
- a utilization-management application

DE-SynPUF does not represent actual Medicare beneficiaries.

The member segments are transparent analytical constructs developed from patterns in the synthetic data and would require independent validation before application to another population.

The local language model can still make interpretation or routing errors. The architecture therefore separates numerical calculation from language-model reasoning and exposes analytical tools and retrieved knowledge sources for traceability.

---

## Known Routing Limitation

Some semantically ambiguous questions can reasonably map to either:

- analytical cohort profiling, or
- knowledge retrieval.

For example:

> What does the persistent high-cost complex cohort look like?

may be interpreted as either a request for observed analytical characteristics or for a cohort description.

The system uses deterministic routing rules for high-confidence intents and local-LLM routing for ambiguous requests. Remaining ambiguity is documented rather than resolved through increasingly brittle keyword rules.

---

## Project Objective

This project demonstrates an approach to agentic healthcare analytics in which:

**LLMs reason, deterministic tools calculate, RAG grounds methodology, and LangGraph orchestrates evidence.**

The emphasis is on combining modern local AI tooling with transparent, validated healthcare analytics rather than allowing a language model to become the source of truth for claims calculations.