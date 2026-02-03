from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from models.paper_struct import PaperSection, PaperStructure
from collections import defaultdict
import re


SECTION_PATTERNS = {
    "abstract": r"\babstract\b",
    "introduction": r"\bintroduction\b",
    "related_work": r"(related work|literature review)",
    "methodology": r"(methodology|method|proposed approach|approach)",
    "experiments": r"(experiments?|results?|evaluation)",
    "conclusion": r"(conclusion|discussion)"
}


# -------------------------------------------------
# Load PDF
# -------------------------------------------------
def load_paper_docs(pdf_path: str) -> list[Document]:
    loader = PyPDFLoader(pdf_path)
    return loader.load()


# -------------------------------------------------
# Extract paper structure
# -------------------------------------------------
def extract_paper_structure_from_docs(docs: list[Document]) -> PaperStructure:
    full_text = "\n".join(doc.page_content for doc in docs)

    structure = PaperStructure()
    structure.title = extract_title(docs)

    # ---- find section positions globally
    section_positions = []

    for name, pattern in SECTION_PATTERNS.items():
        for match in re.finditer(pattern, full_text, re.IGNORECASE):
            section_positions.append((match.start(), name))

    # Sort by position in document
    section_positions.sort(key=lambda x: x[0])

    sections = {}

    for i, (start_pos, section_name) in enumerate(section_positions):
        end_pos = (
            section_positions[i + 1][0]
            if i + 1 < len(section_positions)
            else len(full_text)
        )

        content = full_text[start_pos:end_pos].strip()

        if len(content.split()) < 50:
            continue  # ignore junk sections

        sections[section_name] = PaperSection(
            content=content,
            page_numbers=[],  # can be improved later
            word_count=len(content.split())
        )

    # ---- fallback if nothing detected
    if not sections:
        sections["full_text"] = PaperSection(
            content=full_text[:12000],
            page_numbers=[],
            word_count=len(full_text.split())
        )

    structure.sections = sections
    return structure


# -------------------------------------------------
# Robust title extraction
# -------------------------------------------------
def extract_title(docs: list[Document]) -> str:
    """
    Extract title from first page only (safe)
    """
    if not docs:
        return "Untitled Research Paper"

    first_page = docs[0].page_content

    lines = [
        line.strip()
        for line in first_page.splitlines()
        if 10 < len(line.strip()) < 150
    ]

    # Heuristic: first large, non-noisy line
    for line in lines[:10]:
        if not any(
            bad in line.lower()
            for bad in ["abstract", "introduction", "copyright", "permission", "license"]
        ):
            return line

    return "Untitled Research Paper"
