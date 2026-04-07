from __future__ import annotations

from agents import Agent, Runner

from ..schemas import (
    ExplanationPack,
    LessonPlan,
    NotesPack,
    QuizPack,
    StudyRequest,
    WorkbookOutput,
)
from ..tools import to_pretty_json


class WriterAgentService:
    def __init__(self, model: str) -> None:
        self.agent = Agent(
            name="SmartLearn Workbook Writer Agent",
            model=model,
            instructions=(
                "You synthesize lesson artifacts into a polished markdown workbook for a student. "
                "The workbook must be readable, structured, and practical. Do not include the answer key."
            ),
            output_type=WorkbookOutput,
        )

    def run(
        self,
        request: StudyRequest,
        plan: LessonPlan,
        explanation: ExplanationPack,
        notes: NotesPack,
        quiz: QuizPack,
    ) -> WorkbookOutput:
        prompt = f"""
Create a complete student workbook in markdown.

Learner request:
{to_pretty_json(request)}

Lesson plan:
{to_pretty_json(plan)}

Explanation pack:
{to_pretty_json(explanation)}

Notes pack:
{to_pretty_json(notes)}

Quiz pack:
{to_pretty_json(quiz)}

Requirements for markdown:
- Start with a title and a short learner-oriented summary.
- Include sections for learning objectives, explanation, worked example, misconceptions, glossary, and revision notes.
- End with a short study strategy section.
- Do not expose quiz correct answers in the workbook markdown.
- Use clean markdown headings and bullet points.
""".strip()
        result = Runner.run_sync(self.agent, prompt)
        return result.final_output
