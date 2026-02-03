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


# -------------------------------------------------
# CONCEPT EXTRACTION TOOL
# -------------------------------------------------
@tool
def extract_advanced_concepts(sections_json: str) -> List[Concept]:
    """Comprehensive concept extraction: text + equations + figures + multimodal"""

    sections = json.loads(sections_json)
    all_concepts = []

    # -------- TEXT-BASED CONCEPT EXTRACTION
    text_prompt = ChatPromptTemplate.from_messages([
        ("system", """Expert research paper analyzer. Extract ONLY these research concepts:
REQUIRED FIELDS: name, type, description, confidence (0.0-1.0), section

CONCEPT TYPES:
- ALGORITHM
- TECHNIQUE
- DATASET
- METRIC
- DOMAIN

Return VALID JSON array. No explanations."""),
        ("human", "Analyze these sections: {sections_json}")
    ])

    chain = text_prompt | llm
    response = chain.invoke({
        "sections_json": json.dumps(sections, indent=2, ensure_ascii=False)
    })

    # ✅ FIX 1: Safe JSON parse fallback
    raw_concepts = safe_json_parse(response.content) or []

    for raw_concept in raw_concepts[:40]:
        try:
            all_concepts.append(
                Concept(
                    name=raw_concept.get("name", "unknown").strip(),
                    # ✅ FIX 2: Safe ConceptType casting
                    type=ConceptType(
                        raw_concept.get("type", "TECHNIQUE").upper()
                    ),
                    description=raw_concept.get("description", "").strip(),
                    section=raw_concept.get("section", "unknown"),
                    confidence=float(raw_concept.get("confidence", 0.7))
                )
            )
        except (ValueError, KeyError):
            continue

    # -------- MULTIMODAL CONCEPTS
    full_text = "\n".join(
        section.get("content", "") for section in sections.values()
    )

    all_concepts.extend(extract_equations(full_text))
    all_concepts.extend(extract_figures_tables(full_text))

    # -------- DEDUPLICATE & RANK
    concept_dict = {}
    for concept in all_concepts:
        key = f"{concept.name.lower()}:{concept.type.value}"
        if key not in concept_dict or concept.confidence > concept_dict[key].confidence:
            concept_dict[key] = concept

    return sorted(
        concept_dict.values(),
        key=lambda c: c.confidence,
        reverse=True
    )[:config.MAX_CONCEPTS]


# -------------------------------------------------
# RECOMMENDATION TOOL
# -------------------------------------------------
@tool
def generate_research_recommendations(
    matches: list,
    novelty_score: float
) -> List[str]:
    """Generate actionable academic recommendations"""

    clean_matches = []
    for m in matches:
        if isinstance(m, dict):
            clean_matches.append(m)
        else:
            clean_matches.append(str(m))

    # ✅ FIX 3: Correct similarity key
    high_risk_matches = [
        m for m in clean_matches
        if isinstance(m, dict) and m.get("similarity_score", 0) > 0.8
    ][:3]

    recommendations_prompt = f"""
Generate 5 SPECIFIC academic recommendations.

Novelty score: {novelty_score:.1f}%

High-overlap matches:
{json.dumps(high_risk_matches, indent=2)}

REQUIREMENTS:
1. Cite overlapping work
2. Suggest novelty improvements
3. Extend methodology
4. Recommend datasets or applications

Return numbered list only.
"""

    response = llm.invoke(recommendations_prompt)

    return [
        line.strip("•1234567890.- ").strip()
        for line in response.content.split("\n")
        if len(line.strip()) > 15
    ][:5]


# -------------------------------------------------
# SEARCH ENHANCEMENT TOOL
# -------------------------------------------------
@tool
def enhanced_research_search(
    title: str,
    abstract: str,
    domains: list = None
) -> List[Dict]:
    """Enhanced search with domain-specific queries"""

    domains = domains or []

    # ✅ FIX 4: Correct argument usage
    return research_searcher.search_research_papers(title, abstract)


# -------------------------------------------------
# AGENT SETUP (UNCHANGED)
# -------------------------------------------------
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
    agent=create_react_agent(
        llm=llm,
        tools=extraction_tools,
        prompt=react_prompt
    ),
    tools=extraction_tools,
    verbose=config.DEBUG
)

research_agent = AgentExecutor(
    agent=create_react_agent(
        llm=llm,
        tools=search_tools,
        prompt=react_prompt
    ),
    tools=search_tools,
    verbose=config.DEBUG
)

recommendation_agent = AgentExecutor(
    agent=create_react_agent(
        llm=llm,
        tools=recommend_tools,
        prompt=react_prompt
    ),
    tools=recommend_tools,
    verbose=config.DEBUG
)

# MAIN ORCHESTRATOR (UNCHANGED)
all_tools = extraction_tools + search_tools + recommend_tools
main_orchestrator = AgentExecutor(
    agent=create_react_agent(
        llm=llm,
        tools=all_tools,
        prompt=react_prompt
    ),
    tools=all_tools,
    verbose=config.DEBUG
)
