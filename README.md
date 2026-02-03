# 🧠 Multi-Agent AI System for Internet-Level Academic Plagiarism Detection

> **Idea-level plagiarism detection using Multi-Agent AI, semantic reasoning, and multimodal analysis**  
> (Not just text similarity)

---

## 📌 Overview

Traditional plagiarism detection tools fail when:

- Text is paraphrased
- Structure is changed
- Algorithms or ideas are reused with different wording
- Equations, figures, or methodologies are reformulated

This project introduces a **Multi-Agent AI architecture** that detects **conceptual, methodological, and idea-level plagiarism** by combining:

- Semantic embeddings
- LLM-based reasoning
- Multimodal concept extraction (text, equations, figures)
- Internet research comparison (ArXiv + Web)

---

## 🎯 Key Objectives

- Detect **idea reuse**, not surface text overlap
- Identify **methodological similarity**
- Measure **research novelty**
- Provide **explainable plagiarism reports**
- Gracefully handle missing data and API limits

### 🤖 Agents

| Agent       | Responsibility                                  |
| ----------- | ----------------------------------------------- |
| **Agent 1** | PDF parsing & structure extraction              |
| **Agent 2** | Internet research search (ArXiv, Web)           |
| **Agent 3** | Concept extraction (text + equations + figures) |
| **Agent 4** | Semantic similarity matching                    |
| **Agent 5** | Risk scoring, novelty estimation & reporting    |

## 🧠 What Makes This Different?

| Feature                     | Traditional Tools | This System |
| --------------------------- | ----------------- | ----------- |
| Exact text matching         | ✅                | ❌          |
| Paraphrase detection        | ⚠️ Limited        | ✅          |
| Idea-level similarity       | ❌                | ✅          |
| Algorithm reuse detection   | ❌                | ✅          |
| Equation & figure awareness | ❌                | ✅          |
| Explainable AI output       | ❌                | ✅          |
| Internet-level comparison   | ⚠️ Partial        | ✅          |

## 📥 Input

- **Single research paper (PDF)**

## 📤 Output (Sample)

```json
{
  "submitted_paper_title": "AURA: A Multi-Modal Medical Agent for Clinical Decision Support",
  "total_internet_papers_analyzed": 5,
  "overall_plagiarism_risk": "MEDIUM",
  "novelty_score": 63.4,
  "top_similar_papers": [...],
  "explainability": {...},
  "recommendations": [...]
}
```
