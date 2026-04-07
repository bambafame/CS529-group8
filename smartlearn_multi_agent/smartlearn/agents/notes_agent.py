from __future__ import annotations

from agents import Agent, Runner

from ..schemas import ExplanationPack, LessonPlan, NotesPack, StudyRequest
from ..tools import to_pretty_json


class NotesAgentService:
    def __init__(self, model: str) -> None:
        self.agent = Agent(
            name="SmartLearn Notes Agent",
            model=model,
            instructions=(
                "You create highly usable revision notes from a lesson explanation. "
                "Make them concise, organized, and exam-friendly. Produce high-signal notes, "
                "not long prose. Include a revision checklist and flashcards."
            ),
            output_type=NotesPack,
        )

    def run(
        self,
        request: StudyRequest,
        plan: LessonPlan,
        explanation: ExplanationPack,
    ) -> NotesPack:
        prompt = f"""
Convert the lesson into structured revision notes.

Learner request:
{to_pretty_json(request)}

Lesson plan:
{to_pretty_json(plan)}

Explanation pack:
{to_pretty_json(explanation)}

Requirements:
- Keep notes concise and study-friendly.
- Avoid repetition.
- Make the checklist actionable.
- Make flashcards good for spaced repetition.
""".strip()
        result = Runner.run_sync(self.agent, prompt)
        return result.final_output
