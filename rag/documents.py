from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[1]

KNOWLEDGE_DIR = (
    PROJECT_ROOT
    / "knowledge"
)


def load_markdown_documents() -> list[dict]:
    """
    Load Markdown knowledge files and divide them into
    heading-based semantic chunks.
    """

    documents = []

    for path in sorted(
        KNOWLEDGE_DIR.glob("*.md")
    ):
        text = path.read_text(
            encoding="utf-8"
        )

        sections = re.split(
            r"(?=^#{1,6}\s)",
            text,
            flags=re.MULTILINE,
        )

        for index, section in enumerate(
            sections
        ):
            section = section.strip()

            if not section:
                continue

            documents.append({
                "id": f"{path.stem}_{index}",
                "source": path.name,
                "text": section,
            })

    return documents