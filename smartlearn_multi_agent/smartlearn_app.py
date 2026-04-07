from __future__ import annotations
 
from uuid import uuid4
 
import gradio as gr
 
from smartlearn.config import settings
from smartlearn.manager import SmartLearnManager
from smartlearn.rendering import render_feedback_markdown, render_quiz_markdown
from smartlearn.schemas import StudyRequest
from smartlearn.tools import build_answer_template
 
 
manager = SmartLearnManager(settings)
 
 
def get_event_message(event) -> str:
    if isinstance(event, str):
        return event
    return getattr(event, "message", str(event))
 
 
def get_event_stage(event) -> str:
    if isinstance(event, str):
        return "progress"
    return getattr(event, "stage", "progress")
 
 
def get_event_payload(event):
    if isinstance(event, str):
        return None
    return getattr(event, "payload", None)
 
 
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
 
    progress_lines: list[str] = [
        "### SmartLearn Activity Log",
        "- Starting SmartLearn session...",
        "- Initializing lesson generation...",
    ]
 
    workbook_markdown = "Generating lesson workbook..."
    quiz_markdown = "Generating quiz..."
    answer_template = ""
 
    yield (
        active_session_id,
        "\n".join(progress_lines),
        workbook_markdown,
        quiz_markdown,
        answer_template,
        gr.update(selected=0),
        active_session_id,
    )
 
    result = manager.build_lesson(request, active_session_id)
 
    # Case 1: manager returns (sid, events)
    if isinstance(result, tuple) and len(result) == 2:
        sid, events = result
        for event in events:
            message = get_event_message(event)
            stage = get_event_stage(event)
            payload = get_event_payload(event)
 
            progress_lines.append(f"- {message}")
 
            if stage == "workbook" and payload is not None:
                workbook_markdown = getattr(payload, "markdown", str(payload))
            elif stage == "quiz" and payload is not None:
                quiz_markdown = render_quiz_markdown(payload)
                answer_template = build_answer_template(payload)
 
            yield (
                sid,
                "\n".join(progress_lines),
                workbook_markdown,
                quiz_markdown,
                answer_template,
                gr.update(selected=0),
                sid,
            )
 
    # Case 2: manager is a generator yielding events one by one
    else:
        for event in result:
            message = get_event_message(event)
            stage = get_event_stage(event)
            payload = get_event_payload(event)
 
            progress_lines.append(f"- {message}")
 
            if stage == "workbook" and payload is not None:
                workbook_markdown = getattr(payload, "markdown", str(payload))
            elif stage == "quiz" and payload is not None:
                quiz_markdown = render_quiz_markdown(payload)
                answer_template = build_answer_template(payload)
 
            yield (
                active_session_id,
                "\n".join(progress_lines),
                workbook_markdown,
                quiz_markdown,
                answer_template,
                gr.update(selected=0),
                active_session_id,
            )
 
 
def evaluate_answers_ui(session_id: str, raw_answers: str):
    if not session_id:
        raise gr.Error("No active session found. Build a lesson first.")
 
    if not raw_answers or not raw_answers.strip():
        raise gr.Error("Paste your answers before running evaluation.")
 
    progress_lines: list[str] = [
        "### Evaluation Log",
        "- Checking your answers...",
    ]
    feedback_markdown = "Evaluating your responses..."
 
    yield (
        "\n".join(progress_lines),
        feedback_markdown,
        gr.update(selected=2),
    )
 
    events = manager.evaluate_answers(session_id, raw_answers)
 
    for event in events:
        message = get_event_message(event)
        stage = get_event_stage(event)
        payload = get_event_payload(event)
 
        progress_lines.append(f"- {message}")
 
        if stage == "feedback" and payload is not None:
            feedback_markdown = render_feedback_markdown(payload)
 
        yield (
            "\n".join(progress_lines),
            feedback_markdown,
            gr.update(selected=2),
        )
 
 
custom_css = """
.container {
    max-width: 1400px !important;
    margin: auto;
}
.section-card {
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 14px;
    background: white;
}
.app-subtitle {
    color: #555;
    margin-top: -8px;
    margin-bottom: 10px;
}
"""
 
 
with gr.Blocks(title=settings.app_title, css=custom_css, theme=gr.themes.Soft()) as demo:
    session_state = gr.State("")
 
    gr.Markdown(f"# {settings.app_title}")
    gr.Markdown(
        "Build a lesson, study the explanation, answer the quiz, and receive personalized feedback.",
        elem_classes=["app-subtitle"],
    )
 
    with gr.Row(equal_height=False):
        with gr.Column(scale=1, min_width=350):
            with gr.Group(elem_classes=["section-card"]):
                gr.Markdown("## Lesson Setup")
 
                topic = gr.Textbox(
                    label="Topic",
                    placeholder="Explain recursion",
                )
 
                level = gr.Dropdown(
                    label="Learner Level",
                    choices=["beginner", "intermediate", "advanced"],
                    value="beginner",
                )
 
                learning_goal = gr.Textbox(
                    label="Learning Goal",
                    placeholder="I want to understand the concept well enough to solve simple problems.",
                )
 
                prior_knowledge = gr.Textbox(
                    label="Prior Knowledge",
                    placeholder="I know basic functions but not how recursion works.",
                )
 
                reference_material = gr.Textbox(
                    label="Optional Reference Material",
                    lines=8,
                    placeholder="Paste lecture notes, textbook excerpts, or instructor content here.",
                )
 
                build_button = gr.Button("Build Lesson", variant="primary", size="lg")
 
            with gr.Group(elem_classes=["section-card"]):
                gr.Markdown("## Session")
                active_session = gr.Textbox(
                    label="Session ID",
                    interactive=False,
                    placeholder="A session ID will appear here after lesson generation.",
                )
 
            with gr.Group(elem_classes=["section-card"]):
                gr.Markdown("## Your Answers")
 
                answers = gr.Textbox(
                    label="Answer Submission",
                    lines=10,
                    placeholder="Paste your answers here using the generated q1:, q2:, q3: format.",
                )
 
                with gr.Accordion("Show Answer Template", open=False):
                    answer_template = gr.Textbox(
                        label="Answer Template",
                        lines=8,
                        interactive=False,
                    )
 
                evaluate_button = gr.Button("Evaluate Answers", variant="secondary", size="lg")
 
        with gr.Column(scale=2, min_width=600):
            with gr.Group(elem_classes=["section-card"]):
                progress = gr.Markdown("### SmartLearn Activity Log\n- Waiting to start...")
                evaluation_progress = gr.Markdown("### Evaluation Log\n- No evaluation yet.")
 
            main_tabs = gr.Tabs(selected=0)
 
            with main_tabs:
                with gr.Tab("Workbook"):
                    workbook = gr.Markdown("Your lesson workbook will appear here.")
 
                with gr.Tab("Quiz"):
                    quiz_md = gr.Markdown("Your generated quiz will appear here.")
 
                with gr.Tab("Feedback"):
                    feedback_md = gr.Markdown("Your personalized feedback will appear here after evaluation.")
 
    build_button.click(
        fn=build_lesson_ui,
        inputs=[topic, level, learning_goal, prior_knowledge, reference_material, session_state],
        outputs=[session_state, progress, workbook, quiz_md, answer_template, main_tabs, active_session],
    )
 
    evaluate_button.click(
        fn=evaluate_answers_ui,
        inputs=[session_state, answers],
        outputs=[evaluation_progress, feedback_md, main_tabs],
    )
 
if __name__ == "__main__":
    demo.queue().launch()