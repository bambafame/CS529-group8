from __future__ import annotations

from uuid import uuid4

import gradio as gr

from smartlearn.config import settings
from smartlearn.manager import SmartLearnManager
from smartlearn.rendering import render_feedback_markdown, render_quiz_markdown
from smartlearn.schemas import StudyRequest
from smartlearn.tools import build_answer_template


manager = SmartLearnManager(settings)


def build_lesson_ui(
    topic: str,
    level: str,
    learning_goal: str,
    prior_knowledge: str,
    reference_material: str,
    session_id: str,
):
    if not topic or not topic.strip():
        raise gr.Error("Please enter a topic before building the lesson.")

    active_session_id = session_id or str(uuid4())
    request = StudyRequest(
        topic=topic.strip(),
        level=level,
        learning_goal=learning_goal.strip(),
        prior_knowledge=prior_knowledge.strip(),
        reference_material=reference_material.strip(),
    )

    progress_lines: list[str] = []
    workbook_markdown = ""
    quiz_markdown = ""
    answer_template = ""

    sid, events = manager.build_lesson(request, active_session_id)
    for event in events:
        progress_lines.append(f"- {event.message}")
        if event.stage == "workbook":
            workbook_markdown = event.payload.markdown
        elif event.stage == "quiz":
            quiz_markdown = render_quiz_markdown(event.payload)
            answer_template = build_answer_template(event.payload)
        yield sid, "\n".join(progress_lines), workbook_markdown, quiz_markdown, answer_template


def evaluate_answers_ui(session_id: str, raw_answers: str):
    if not session_id:
        raise gr.Error("No active session found. Build a lesson first.")
    if not raw_answers or not raw_answers.strip():
        raise gr.Error("Paste your answers before running evaluation.")

    progress_lines: list[str] = []
    feedback_markdown = ""

    events = manager.evaluate_answers(session_id, raw_answers)
    for event in events:
        progress_lines.append(f"- {event.message}")
        if event.stage == "feedback":
            feedback_markdown = render_feedback_markdown(event.payload)
        yield "\n".join(progress_lines), feedback_markdown


with gr.Blocks(title=settings.app_title) as demo:
    session_state = gr.State("")

    gr.Markdown(f"# {settings.app_title}")
    gr.Markdown(
        "Build a lesson, generate revision material, answer the quiz, and receive personalized feedback."
    )

    with gr.Row():
        with gr.Column(scale=1):
            topic = gr.Textbox(label="Topic", placeholder="Explain recursion")
            level = gr.Dropdown(
                label="Learner level",
                choices=["beginner", "intermediate", "advanced"],
                value="beginner",
            )
            learning_goal = gr.Textbox(
                label="Learning goal",
                placeholder="I want to understand the concept well enough to solve simple problems.",
            )
            prior_knowledge = gr.Textbox(
                label="Prior knowledge",
                placeholder="I know basic functions but not how recursion works.",
            )
            reference_material = gr.Textbox(
                label="Optional reference material",
                lines=10,
                placeholder="Paste lecture notes, textbook excerpts, or instructor content here.",
            )
            build_button = gr.Button("Build Lesson", variant="primary")
            active_session = gr.Textbox(label="Session ID", interactive=False)

        with gr.Column(scale=2):
            progress = gr.Markdown(label="Progress")
            workbook = gr.Markdown(label="Workbook")

    with gr.Row():
        quiz_md = gr.Markdown(label="Quiz")

    with gr.Row():
        answers = gr.Textbox(
            label="Your answers",
            lines=8,
            placeholder="Use the generated q1:, q2:, q3: answer template.",
        )
        answer_template = gr.Textbox(label="Answer template", lines=8, interactive=False)

    evaluate_button = gr.Button("Evaluate Answers")
    evaluation_progress = gr.Markdown(label="Evaluation progress")
    feedback_md = gr.Markdown(label="Feedback")

    build_button.click(
        fn=build_lesson_ui,
        inputs=[topic, level, learning_goal, prior_knowledge, reference_material, session_state],
        outputs=[session_state, progress, workbook, quiz_md, answer_template],
    ).then(lambda sid: sid, inputs=session_state, outputs=active_session)

    evaluate_button.click(
        fn=evaluate_answers_ui,
        inputs=[session_state, answers],
        outputs=[evaluation_progress, feedback_md],
    )


if __name__ == "__main__":
    demo.queue().launch()
