from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field


LevelType = Literal["beginner", "intermediate", "advanced"]
QuestionType = Literal["mcq", "true_false", "short_answer"]


class StudyRequest(BaseModel):
    topic: str = Field(..., description="The concept or topic to study.")
    level: LevelType = Field(..., description="The learner proficiency level.")
    learning_goal: str = Field(
        default="",
        description="The outcome the learner wants to achieve after the lesson.",
    )
    prior_knowledge: str = Field(
        default="",
        description="What the learner already knows about the topic.",
    )
    reference_material: str = Field(
        default="",
        description="Optional grounded material such as lecture notes or textbook excerpts.",
    )


class ReferenceSnippet(BaseModel):
    snippet_id: str = Field(..., description="Identifier for the retrieved reference snippet.")
    content: str = Field(..., description="Relevant extracted reference text.")
    relevance_reason: str = Field(..., description="Why the snippet matters to the topic.")


class LessonPlan(BaseModel):
    topic: str
    learner_level: LevelType
    lesson_title: str
    learning_objectives: list[str]
    prerequisites: list[str]
    focus_areas: list[str]
    recommended_teaching_strategy: str
    quiz_difficulty: str
    retrieved_context_summary: str


class GlossaryTerm(BaseModel):
    term: str
    definition: str


class ExplanationPack(BaseModel):
    overview: str
    step_by_step_explanation: list[str]
    worked_example: str
    analogy: str
    common_misconceptions: list[str]
    glossary: list[GlossaryTerm]


class Flashcard(BaseModel):
    front: str
    back: str


class NotesPack(BaseModel):
    one_paragraph_summary: str
    key_points: list[str]
    structured_notes: list[str]
    revision_checklist: list[str]
    flashcards: list[Flashcard]


class QuizQuestion(BaseModel):
    question_id: str
    question_type: QuestionType
    prompt: str
    options: list[str] = Field(default_factory=list)
    correct_answer: str
    explanation: str
    difficulty: str
    hint: str


class QuizPack(BaseModel):
    title: str
    instructions: str
    questions: list[QuizQuestion]


class WorkbookOutput(BaseModel):
    title: str
    learner_summary: str
    markdown: str


class AutoGradeHint(BaseModel):
    question_id: str
    detected_answer: str
    matched_correct_answer: bool
    notes: str


class QuestionFeedback(BaseModel):
    question_id: str
    score_label: str
    feedback: str
    correction: str


class FeedbackPack(BaseModel):
    score_percent: float
    mastery_level: str
    strengths: list[str]
    improvement_areas: list[str]
    per_question_feedback: list[QuestionFeedback]
    next_steps: list[str]
    recommended_next_difficulty: str


@dataclass(slots=True)
class ProgressEvent:
    stage: str
    message: str
    payload: object | None = None


@dataclass(slots=True)
class SessionRecord:
    session_id: str
    request: StudyRequest | None = None
    plan: LessonPlan | None = None
    explanation: ExplanationPack | None = None
    notes: NotesPack | None = None
    quiz: QuizPack | None = None
    workbook: WorkbookOutput | None = None
    reference_snippets: list[ReferenceSnippet] = field(default_factory=list)
    last_feedback: FeedbackPack | None = None
    answer_history: list[str] = field(default_factory=list)
