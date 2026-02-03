import json
import re
from models.analysis_result import Explainability


# -------------------------------------------------
# Safe JSON parser
# -------------------------------------------------
def safe_json_parse(content: str):
    """
    Safely parse JSON from string or markdown.
    Returns None on failure (explicit, not silent).
    """
    if not content:
        return None

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        json_match = re.search(
            r'```json\s*(.*?)\s*```',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                return None

    return None


# -------------------------------------------------
# Explainability formatter
# -------------------------------------------------
def format_explainability(matches):
    """
    Build explainability object from similarity matches
    """
    phrases = []
    weights = {}
    false_positives = 0

    if not matches:
        return Explainability(
            top_contributing_phrases=[],
            attention_weights={},
            false_positives_filtered=0
        )

    for idx, match in enumerate(matches[:10]):
        # ------------------------
        # Dict-based match
        # ------------------------
        if isinstance(match, dict):
            concept = match.get("user_concept", "")
            similarity = float(match.get("similarity_score", 0.5))

            if not concept:
                continue

            # Preserve more semantic context (80 chars)
            phrase = concept[:80].strip()

            # Ensure unique keys
            key = f"{idx}_{phrase}"

            phrases.append(phrase)
            weights[key] = similarity

            if match.get("is_false_positive", False):
                false_positives += 1

        # ------------------------
        # Object-based match
        # ------------------------
        else:
            phrase = getattr(match, "phrase", "")[:80].strip()
            similarity = float(getattr(match, "weight", 0.5))

            if not phrase:
                continue

            key = f"{idx}_{phrase}"

            phrases.append(phrase)
            weights[key] = similarity

            if getattr(match, "is_false_positive", False):
                false_positives += 1

    return Explainability(
        top_contributing_phrases=phrases,
        attention_weights=weights,
        false_positives_filtered=false_positives
    )
