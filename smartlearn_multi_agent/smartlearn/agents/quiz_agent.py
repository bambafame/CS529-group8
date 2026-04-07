from __future__ import annotations

from agents import Agent, Runner

from ..schemas import ExplanationPack, LessonPlan, QuizPack, StudyRequest
from ..tools import to_pretty_json


class QuizAgentService:
    def __init__(self, model: str) -> None:
        self.agent = Agent(
            name="SmartLearn Quiz Agent",
            model=model,
            instructions=(
                "You generate learning quizzes that accurately test understanding. "
                "Create a balanced set of questions with clear answers and explanations. "
                "Make question IDs q1, q2, q3, ... and include hints."
            ),
            output_type=QuizPack,
        )

    def run(
        self,
        request: StudyRequest,
        plan: LessonPlan,
        explanation: ExplanationPack,
    ) -> QuizPack:
        prompt = f"""
Create a quiz for the learner.

Learner request:
{to_pretty_json(request)}

Lesson plan:
{to_pretty_json(plan)}

Explanation pack:
{to_pretty_json(explanation)}

Requirements:
- Create 5 questions total.
- Include a mix of MCQ, true/false, and short-answer when appropriate.
- Every question must test an important concept from the lesson.
- Provide the correct answer and a short explanation.
- Set difficulty using the plan's quiz difficulty.
- Ensure question IDs are q1, q2, q3, q4, q5.
""".strip()
        result = Runner.run_sync(self.agent, prompt)
        return result.final_output
