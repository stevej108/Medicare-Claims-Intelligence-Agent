import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from agents.workflow import (
    ask_claims_agent,
)


st.set_page_config(
    page_title=(
        "Medicare Claims Intelligence Agent"
    ),
    page_icon="🏥",
    layout="wide",
)

st.title(
    "Medicare Claims Intelligence Agent"
)

st.caption(
    "Agentic analytics over synthetic CMS DE-SynPUF "
    "Medicare claims data"
)

st.info(
    "This application uses synthetic CMS DE-SynPUF "
    "data. Results demonstrate analytical methodology "
    "and do not represent actual Medicare beneficiaries."
)

st.subheader(
    "Example questions"
)

examples = [
    (
        "What percentage of member-years "
        "had inpatient utilization?"
    ),
    (
        "Describe the pharmacy-intensive "
        "chronic population."
    ),
    (
        "What share of positive spending "
        "comes from the top 10%?"
    ),
    (
        "How is total annual cost calculated?"
    ),
    (
        "Compare persistent high-cost complex members "
        "with pharmacy-intensive chronic members, "
        "explain how each cohort is defined, and summarize "
        "the main utilization differences."
    ),
]

for example in examples:
    st.markdown(
        f"- {example}"
    )

question = st.chat_input(
    "Ask a Medicare claims analytics question..."
)

if question:

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):

        with st.spinner(
            "Analyzing synthetic claims data..."
        ):

            try:
                response = ask_claims_agent(
                    question
                )

            except Exception as exc:
                st.error(
                    "The claims agent could not "
                    "complete this request."
                )

                with st.expander(
                    "Technical details"
                ):
                    st.exception(exc)

                st.stop()

        # ---------------------------
        # Main answer
        # ---------------------------

        st.markdown(
            response.answer
        )

        # ---------------------------
        # Analysis trace
        # ---------------------------

        with st.expander(
            "Analysis trace"
        ):

            st.write(
                f"**Mode:** "
                f"{response.mode.value}"
            )

            if (
                response.analytical_tool
                is not None
            ):
                st.write(
                    f"**Analytical tool:** "
                    f"{response.analytical_tool}"
                )

                if (
                    response.analytical_arguments
                ):
                    st.write(
                        "**Arguments:**"
                    )

                    st.json(
                        response.analytical_arguments
                    )

            if response.sources:

                st.write(
                    "**Knowledge sources:**"
                )

                for source in response.sources:
                    st.write(
                        f"- {source}"
                    )

        # ---------------------------
        # Synthetic-data disclaimer
        # ---------------------------

        st.caption(
            response.synthetic_data_notice
        )