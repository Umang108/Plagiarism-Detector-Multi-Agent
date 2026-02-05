from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from src.config import llm, config
from src.multimodal import extract_equations, extract_figures_tables
from src.search_tools import research_searcher
from src.utils import safe_json_parse
from models.paper_struct import Concept, ConceptType
from typing import List, Dict
import json


# =================================================
# CONCEPT EXTRACTION TOOL
# =================================================
@tool
def extract_advanced_concepts(sections_json: str) -> List[Concept]:
    """
    Robust multimodal concept extraction with fallback guarantees
    """

    sections = json.loads(sections_json)
    all_concepts: List[Concept] = []

    # ---------- LLM TEXT CONCEPT EXTRACTION ----------
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are an expert research paper analyzer.

Extract research concepts as JSON.
Each item MUST contain:
- name
- type (ALGORITHM | TECHNIQUE | DATASET | METRIC | DOMAIN)
- description
- confidence (0.0–1.0)
- section

Return ONLY a valid JSON array.
"""),
        ("human", "{sections_json}")
    ])

    response = (prompt | llm).invoke({
        "sections_json": json.dumps(sections, indent=2)
    })

    raw_concepts = safe_json_parse(response.content) or []

    for rc in raw_concepts[:40]:
        try:
            all_concepts.append(
                Concept(
                    name=rc.get("name", "unknown"),
                    type=ConceptType(rc.get("type", "TECHNIQUE").upper()),
                    description=rc.get("description", ""),
                    section=rc.get("section", "unknown"),
                    confidence=float(rc.get("confidence", 0.7))
                )
            )
        except Exception:
            continue

    # ---------- MULTIMODAL CONCEPTS ----------
    full_text = "\n".join(
        section.get("content", "") for section in sections.values()
    )

    all_concepts.extend(extract_equations(full_text))
    all_concepts.extend(extract_figures_tables(full_text))

    # ---------- FALLBACK (CRITICAL FIX) ----------
    # Ensures FAISS has enough semantic signal
    if len(all_concepts) < 6:
        for sec_name, sec in sections.items():
            content = sec.get("content", "")
            if len(content) > 300:
                all_concepts.append(
                    Concept(
                        name=f"{sec_name} methodology content",
                        type=ConceptType.DOMAIN,
                        description=content[:300],
                        section=sec_name,
                        confidence=0.6
                    )
                )

    # ---------- DEDUPLICATION ----------
    unique = {}
    for c in all_concepts:
        key = f"{c.name.lower()}:{c.type.value}"
        if key not in unique or c.confidence > unique[key].confidence:
            unique[key] = c

    final_concepts = sorted(
        unique.values(),
        key=lambda c: c.confidence,
        reverse=True
    )[:config.MAX_CONCEPTS]

    print(f"✅ Extracted {len(final_concepts)} concepts")
    return final_concepts


# =================================================
# RECOMMENDATION TOOL
# =================================================
@tool
def generate_research_recommendations(
    matches: list,
    novelty_score: float
) -> List[str]:
    """
    Generates academic recommendations from overlap analysis
    """

    high_overlap = [
        m for m in matches
        if isinstance(m, dict) and m.get("similarity_score", 0) > 0.8
    ][:3]

    prompt = f"""
Generate 5 concrete academic recommendations.

Novelty score: {novelty_score:.1f}%

High overlap evidence:
{json.dumps(high_overlap, indent=2)}

Rules:
1. Cite overlapping ideas
2. Suggest novelty improvements
3. Extend methodology
4. Recommend datasets/applications

Return numbered list only.
"""

    response = llm.invoke(prompt)

    return [
        line.strip("•1234567890.- ").strip()
        for line in response.content.split("\n")
        if len(line.strip()) > 15
    ][:5]


# =================================================
# SEARCH TOOL
# =================================================
@tool
def enhanced_research_search(
    title: str,
    abstract: str,
    domains: list = None
) -> List[Dict]:
    """
    Internet research search (Arxiv + Web)
    """
    return research_searcher.search_research_papers(title, abstract)


# =================================================
# AGENT SETUP (UNCHANGED WORKFLOW)
# =================================================
extraction_tools = [extract_advanced_concepts]
search_tools = [enhanced_research_search]
recommend_tools = [generate_research_recommendations]

react_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an intelligent research assistant.

You have access to the following tools:
{tools}

Tool names:
{tool_names}

Use the tools ONLY when necessary.
Follow the ReAct pattern strictly.
"""),
    ("human", "{input}"),
    ("assistant", "{agent_scratchpad}")
])


concept_agent = AgentExecutor(
    agent=create_react_agent(llm, extraction_tools, react_prompt),
    tools=extraction_tools,
    verbose=config.DEBUG
)

research_agent = AgentExecutor(
    agent=create_react_agent(llm, search_tools, react_prompt),
    tools=search_tools,
    verbose=config.DEBUG
)

recommendation_agent = AgentExecutor(
    agent=create_react_agent(llm, recommend_tools, react_prompt),
    tools=recommend_tools,
    verbose=config.DEBUG
)

# MAIN ORCHESTRATOR
all_tools = extraction_tools + search_tools + recommend_tools
main_orchestrator = AgentExecutor(
    agent=create_react_agent(llm, all_tools, react_prompt),
    tools=all_tools,
    verbose=config.DEBUG
)
