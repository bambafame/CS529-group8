from __future__ import annotations

from agents import Agent, Runner

from ..schemas import ExplanationPack, LessonPlan, StudyRequest
from ..tools import to_pretty_json


class ExplainerAgentService:
    def __init__(self, model: str) -> None:
        self.agent = Agent(
            name="SmartLearn Concept Explainer Agent",
            model=model,
            instructions=(
                "You are an expert teaching assistant. Explain the topic clearly for the learner's level. "
                "Use plain language first, then add precision. Include one worked example, one analogy, "
                "common misconceptions, and a small glossary. Prefer conceptual clarity over unnecessary jargon."
            ),
            output_type=ExplanationPack,
        )

    def run(
        self,
        request: StudyRequest,
        plan: LessonPlan,
        reference_context: str,
    ) -> ExplanationPack:
        prompt = f"""
Teach the learner using the lesson plan below.

Learner request:
{to_pretty_json(request)}

Lesson plan:
{to_pretty_json(plan)}

Reference context:
{reference_context}

Requirements:
- The overview should be direct and level-appropriate.
- The step-by-step explanation must have logical progression.
- The worked example must be concrete.
- The analogy must be intuitive and memorable.
- Misconceptions should be realistic mistakes learners make.
- Glossary definitions must be brief.
""".strip()
        result = Runner.run_sync(self.agent, prompt)
        return result.final_output
