from langchain_core.tools import tool
from models.paper_struct import Concept, ConceptType
import re


# -------------------------------------------------
# Equation Extraction Tool
# -------------------------------------------------
@tool
def extract_equations(text: str) -> list[Concept]:
    """Extract LaTeX and mathematical equations from text"""

    equation_patterns = [
        r'\$\$([\s\S]{10,500}?)\$\$',     # Display math
        r'\$(?!\$)([^$\n]{10,200})\$',    # Inline math (safer)
        r'(?:Eq\.?|Equation)\s*\(?\d+[\.\d]*\)?\s*[:=]\s*([^\n.]{10,300})'
    ]

    math_keywords = [
        '\\', 'sum', 'int', 'frac', 'argmin', 'argmax',
        'log', 'exp', 'min', 'max', '^', '_'
    ]

    seen = set()
    equations: list[Concept] = []

    for pattern in equation_patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)

        for match in matches:
            eq_text = match.strip()

            if (
                len(eq_text) < 10 or
                not any(k in eq_text.lower() for k in math_keywords)
            ):
                continue

            # De-duplication
            key = re.sub(r'\s+', ' ', eq_text)[:120]
            if key in seen:
                continue
            seen.add(key)

            equations.append(
                Concept(
                    name=f"Equation: {eq_text[:60]}...",
                    type=ConceptType.EQUATION,
                    description=f"Mathematical formulation: {eq_text}",
                    section="methodology",
                    confidence=0.92
                )
            )

    return equations[:12]


# -------------------------------------------------
# Figure & Table Extraction Tool
# -------------------------------------------------
@tool
def extract_figures_tables(text: str) -> list[Concept]:
    """Extract figure and table references with descriptions"""

    patterns = {
        ConceptType.FIGURE: [
            r'(?:Figure|Fig)\.?\s*(\d+[a-zA-Z]?)\s*(?:[:\-]|shows?|presents?|illustrates?)\s*([^\n.]{15,150})'
        ],
        ConceptType.TABLE: [
            r'(?:Table)\s*(\d+[a-zA-Z]?)\s*(?:[:\-]|shows?|lists?)\s*([^\n.]{15,150})'
        ]
    }

    seen = set()
    visuals: list[Concept] = []

    for ctype, regex_list in patterns.items():
        for pattern in regex_list:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)

            for idx, desc in matches:
                desc_clean = desc.strip()

                key = f"{ctype.value}-{idx}-{desc_clean[:40]}"
                if key in seen:
                    continue
                seen.add(key)

                visuals.append(
                    Concept(
                        name=f"{ctype.value.title()} {idx}",
                        type=ctype,
                        description=desc_clean[:120],
                        section="results",
                        confidence=0.85
                    )
                )

    return visuals[:15]
