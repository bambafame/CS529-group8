from __future__ import annotations

from agents import Agent, Runner

from ..schemas import FeedbackPack, LessonPlan, QuizPack, StudyRequest
from ..tools import to_pretty_json


class FeedbackAgentService:
    def __init__(self, model: str) -> None:
        self.agent = Agent(
            name="SmartLearn Feedback Agent",
            model=model,
            instructions=(
                "You are a supportive evaluator. Grade answers fairly, explain mistakes clearly, "
                "and recommend next steps. Use objective auto-grading hints when they exist, but also "
                "use semantic judgment for short answers. Be constructive and specific."
            ),
            output_type=FeedbackPack,
        )

    def run(
        self,
        request: StudyRequest,
        plan: LessonPlan,
        quiz: QuizPack,
        student_answers: dict[str, str],
        auto_grade_hints: object,
    ) -> FeedbackPack:
        prompt = f"""
Evaluate the learner answers.

Learner request:
{to_pretty_json(request)}

Lesson plan:
{to_pretty_json(plan)}

Quiz pack:
{to_pretty_json(quiz)}

Student answers:
{to_pretty_json(student_answers)}

Auto-grade hints:
{to_pretty_json(auto_grade_hints)}

Requirements:
- Use objective hints for MCQ and true/false where appropriate.
- Grade short answers on meaning, not exact wording.
- Provide per-question feedback.
- Give strengths, improvement areas, and clear next steps.
- Recommend next difficulty based on performance.
""".strip()
        result = Runner.run_sync(self.agent, prompt)
        return result.final_output
