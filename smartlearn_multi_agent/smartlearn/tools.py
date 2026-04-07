from __future__ import annotations

import json
import re
from typing import Iterable

from .schemas import AutoGradeHint, QuizPack, ReferenceSnippet


def normalize_level(level: str) -> str:
    cleaned = (level or "beginner").strip().lower()
    if cleaned in {"beginner", "intermediate", "advanced"}:
        return cleaned
    aliases = {
        "basic": "beginner",
        "novice": "beginner",
        "medium": "intermediate",
        "mid": "intermediate",
        "expert": "advanced",
    }
    return aliases.get(cleaned, "beginner")


def compact_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def chunk_text(text: str, chunk_chars: int = 1000, overlap: int = 120) -> list[str]:
    cleaned = compact_text(text)
    if not cleaned:
        return []
    if len(cleaned) <= chunk_chars:
        return [cleaned]

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_chars)
        chunks.append(cleaned[start:end])
        if end == len(cleaned):
            break
        start = max(0, end - overlap)
    return chunks


def keyword_overlap_score(query: str, chunk: str) -> int:
    query_terms = {
        token
        for token in re.findall(r"[A-Za-z0-9_\-]+", query.lower())
        if len(token) > 2
    }
    chunk_terms = set(re.findall(r"[A-Za-z0-9_\-]+", chunk.lower()))
    return len(query_terms & chunk_terms)


def retrieve_reference_snippets(
    query: str,
    reference_material: str,
    *,
    k: int = 3,
    chunk_chars: int = 1000,
) -> list[ReferenceSnippet]:
    chunks = chunk_text(reference_material, chunk_chars=chunk_chars)
    if not chunks:
        return []

    ranked = sorted(
        enumerate(chunks, start=1),
        key=lambda item: keyword_overlap_score(query, item[1]),
        reverse=True,
    )

    snippets: list[ReferenceSnippet] = []
    for rank, (index, chunk) in enumerate(ranked[:k], start=1):
        snippets.append(
            ReferenceSnippet(
                snippet_id=f"ref_{rank}_{index}",
                content=chunk,
                relevance_reason=(
                    "Selected because it overlaps strongly with the learner topic, goals, "
                    "or prerequisite vocabulary."
                ),
            )
        )
    return snippets


def snippets_to_prompt(snippets: Iterable[ReferenceSnippet]) -> str:
    items = list(snippets)
    if not items:
        return "No grounded reference material provided."
    sections = []
    for snippet in items:
        sections.append(
            f"[{snippet.snippet_id}] {snippet.content}\nWhy relevant: {snippet.relevance_reason}"
        )
    return "\n\n".join(sections)


def to_pretty_json(data: object) -> str:
    if hasattr(data, "model_dump"):
        payload = data.model_dump()
    elif isinstance(data, list):
        payload = [item.model_dump() if hasattr(item, "model_dump") else item for item in data]
    else:
        payload = data
    return json.dumps(payload, indent=2, ensure_ascii=False)


def build_answer_template(quiz: QuizPack) -> str:
    lines = []
    for question in quiz.questions:
        lines.append(f"{question.question_id}: ")
    return "\n".join(lines)


def parse_student_answers(raw_answers: str, quiz: QuizPack) -> dict[str, str]:
    answers: dict[str, str] = {}
    current_key: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer, current_key
        if current_key is not None:
            answers[current_key] = " ".join(part.strip() for part in buffer).strip()
        buffer = []

    valid_ids = {question.question_id for question in quiz.questions}
    for line in raw_answers.splitlines():
        match = re.match(r"^\s*(q\d+)\s*[:\-]\s*(.*)$", line.strip(), flags=re.IGNORECASE)
        if match:
            flush()
            key = match.group(1).lower()
            current_key = key if key in valid_ids else None
            if current_key is not None:
                buffer.append(match.group(2))
        elif current_key is not None:
            buffer.append(line)
    flush()

    for question in quiz.questions:
        answers.setdefault(question.question_id, "")
    return answers


def normalize_answer(answer: str) -> str:
    return re.sub(r"\s+", " ", (answer or "").strip().lower())


def auto_grade_answers(quiz: QuizPack, answers: dict[str, str]) -> list[AutoGradeHint]:
    hints: list[AutoGradeHint] = []
    for question in quiz.questions:
        student_answer = answers.get(question.question_id, "")
        correct = normalize_answer(question.correct_answer)
        student = normalize_answer(student_answer)

        if question.question_type in {"mcq", "true_false"}:
            matched = student == correct
            notes = (
                "Exact match grading applied because this is an objective question."
                if student_answer
                else "No answer provided for this objective question."
            )
        else:
            matched = False
            notes = (
                "Subjective answer: use semantic grading and rubric-based feedback."
                if student_answer
                else "No answer provided for this subjective question."
            )

        hints.append(
            AutoGradeHint(
                question_id=question.question_id,
                detected_answer=student_answer,
                matched_correct_answer=matched,
                notes=notes,
            )
        )
    return hints
