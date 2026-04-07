from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from agents import trace

from .agents.explainer_agent import ExplainerAgentService
from .agents.feedback_agent import FeedbackAgentService
from .agents.notes_agent import NotesAgentService
from .agents.planner_agent import PlannerAgentService
from .agents.quiz_agent import QuizAgentService
from .agents.writer_agent import WriterAgentService
from .config import Settings, settings
from .schemas import ProgressEvent, StudyRequest
from .session_store import SessionStore
from .tools import (
    auto_grade_answers,
    normalize_level,
    parse_student_answers,
    retrieve_reference_snippets,
    snippets_to_prompt,
)


class SmartLearnManager:
    def __init__(self, config: Settings | None = None) -> None:
        self.settings = config or settings
        self.settings.validate()
        model = self.settings.model

        self.sessions = SessionStore()
        self.planner_agent = PlannerAgentService(model)
        self.explainer_agent = ExplainerAgentService(model)
        self.notes_agent = NotesAgentService(model)
        self.quiz_agent = QuizAgentService(model)
        self.writer_agent = WriterAgentService(model)
        self.feedback_agent = FeedbackAgentService(model)

    def build_lesson(
        self, request: StudyRequest, session_id: str | None = None
    ) -> tuple[str, list[ProgressEvent]]:
        normalized_request = request.model_copy(
            update={"level": normalize_level(request.level)}
        )
        sid = session_id or str(uuid4())
        record = self.sessions.get_or_create(sid)
        record.request = normalized_request

        snippets = retrieve_reference_snippets(
            query=" ".join(
                filter(
                    None,
                    [
                        normalized_request.topic,
                        normalized_request.learning_goal,
                        normalized_request.prior_knowledge,
                    ],
                )
            ),
            reference_material=normalized_request.reference_material,
            k=self.settings.max_reference_snippets,
            chunk_chars=self.settings.reference_chunk_chars,
        )
        record.reference_snippets = snippets
        reference_context = snippets_to_prompt(snippets)

        events: list[ProgressEvent] = [
            ProgressEvent("start", "SmartLearn session started."),
            ProgressEvent(
                "grounding",
                (
                    "Grounded the lesson with user-provided reference material."
                    if snippets
                    else "No reference material provided; proceeding with general teaching mode."
                ),
            ),
        ]

        with trace(f"smartlearn_lesson_{sid}"):
            record.plan = self.planner_agent.run(normalized_request, reference_context)
            events.append(
                ProgressEvent("plan", "Planner Agent created the lesson plan.", record.plan)
            )

            record.explanation = self.explainer_agent.run(
                normalized_request,
                record.plan,
                reference_context,
            )
            events.append(
                ProgressEvent(
                    "explain",
                    "Explainer Agent produced the lesson explanation.",
                    record.explanation,
                )
            )

            events.append(
                ProgressEvent(
                    "parallel", "Generating revision notes and quiz in parallel."
                )
            )
            with ThreadPoolExecutor(max_workers=2) as pool:
                notes_future = pool.submit(
                    self.notes_agent.run,
                    normalized_request,
                    record.plan,
                    record.explanation,
                )
                quiz_future = pool.submit(
                    self.quiz_agent.run,
                    normalized_request,
                    record.plan,
                    record.explanation,
                )
                record.notes = notes_future.result()
                record.quiz = quiz_future.result()

            events.append(
                ProgressEvent("notes", "Notes Agent completed the revision notes.", record.notes)
            )
            events.append(
                ProgressEvent("quiz", "Quiz Agent created the assessment quiz.", record.quiz)
            )

            record.workbook = self.writer_agent.run(
                normalized_request,
                record.plan,
                record.explanation,
                record.notes,
                record.quiz,
            )
            events.append(
                ProgressEvent(
                    "workbook",
                    "Writer Agent synthesized the final student workbook.",
                    record.workbook,
                )
            )

        events.append(
            ProgressEvent("done", "SmartLearn lesson package is ready.", record.workbook)
        )
        return sid, events

    def evaluate_answers(self, session_id: str, raw_answers: str) -> list[ProgressEvent]:
        record = self.sessions.get(session_id)
        if record is None or record.request is None or record.plan is None or record.quiz is None:
            raise ValueError(
                "No active lesson was found for this session. Build a lesson first."
            )

        record.answer_history.append(raw_answers)
        events: list[ProgressEvent] = [
            ProgressEvent("start", "Answer evaluation started."),
        ]

        student_answers = parse_student_answers(raw_answers, record.quiz)
        auto_hints = auto_grade_answers(record.quiz, student_answers)
        events.append(
            ProgressEvent(
                "autograde",
                "Applied light deterministic grading to objective questions.",
                auto_hints,
            )
        )

        with trace(f"smartlearn_feedback_{session_id}"):
            record.last_feedback = self.feedback_agent.run(
                record.request,
                record.plan,
                record.quiz,
                student_answers,
                auto_hints,
            )

        events.append(
            ProgressEvent(
                "feedback",
                "Feedback Agent completed the learner evaluation.",
                record.last_feedback,
            )
        )
        events.append(
            ProgressEvent("done", "Evaluation complete.", record.last_feedback)
        )
        return events
