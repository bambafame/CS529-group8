from __future__ import annotations

from .schemas import FeedbackPack, QuizPack


def render_quiz_markdown(quiz: QuizPack) -> str:
    lines = [f"# {quiz.title}", "", quiz.instructions, ""]
    for index, question in enumerate(quiz.questions, start=1):
        lines.append(f"## {index}. {question.prompt}")
        lines.append(f"Type: **{question.question_type.replace('_', ' ').title()}**")
        lines.append(f"Difficulty: **{question.difficulty}**")
        if question.options:
            for option in question.options:
                lines.append(f"- {option}")
        lines.append(f"Hint: {question.hint}")
        lines.append("")
    return "\n".join(lines)


def render_feedback_markdown(feedback: FeedbackPack) -> str:
    lines = [
        "# Quiz Feedback",
        "",
        f"**Score:** {feedback.score_percent:.1f}%",
        f"**Mastery level:** {feedback.mastery_level}",
        "",
        "## Strengths",
    ]
    lines.extend(f"- {item}" for item in feedback.strengths)
    lines.extend(["", "## Improvement Areas"])
    lines.extend(f"- {item}" for item in feedback.improvement_areas)
    lines.extend(["", "## Per-Question Feedback"])
    for item in feedback.per_question_feedback:
        lines.extend(
            [
                f"### {item.question_id}",
                f"**Result:** {item.score_label}",
                item.feedback,
                f"**Correction:** {item.correction}",
                "",
            ]
        )
    lines.extend(["## Recommended Next Steps"])
    lines.extend(f"- {item}" for item in feedback.next_steps)
    lines.append("")
    lines.append(
        f"**Recommended next difficulty:** {feedback.recommended_next_difficulty}"
    )
    return "\n".join(lines)
