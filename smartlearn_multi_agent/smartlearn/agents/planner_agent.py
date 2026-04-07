from __future__ import annotations

from agents import Agent, Runner

from ..schemas import LessonPlan, StudyRequest
from ..tools import to_pretty_json


class PlannerAgentService:
    def __init__(self, model: str) -> None:
        self.agent = Agent(
            name="SmartLearn Planner Agent",
            model=model,
            instructions=(
                "You are a lesson planning agent for an adaptive learning system. "
                "Your job is to transform a learner request into a structured lesson plan. "
                "Create a practical plan with clear learning objectives, prerequisites, "
                "focus areas, a teaching strategy, and an appropriate quiz difficulty. "
                "Ground the plan in any provided reference material summary when available."
            ),
            output_type=LessonPlan,
        )

    def run(self, request: StudyRequest, reference_context: str) -> LessonPlan:
        prompt = f"""
Create a lesson plan for the following learner request.

Learner request:
{to_pretty_json(request)}

Reference context:
{reference_context}

Requirements:
- Return a concise but useful lesson plan.
- Match the learner level.
- Use the learning goal and prior knowledge to decide emphasis.
- Keep prerequisites realistic and not too many.
- Set quiz difficulty appropriate to the learner level.
""".strip()
        result = Runner.run_sync(self.agent, prompt)
        return result.final_output
