# SmartLearn Multi-Agent Learning System

SmartLearn is a production-style multi-agent learning assistant designed for teaching, revision, quiz generation, and feedback.

Instead of focusing on information retrieval or report writing, SmartLearn builds a complete learning experience: it plans a lesson, explains the concept, generates structured notes, creates a quiz, and evaluates student answers.

## Why this design

SmartLearn uses a centralized orchestration model with specialized agents working together to deliver a full learning pipeline:

1. **Planner Agent** builds a lesson plan from the topic, learner level, and goals.
2. **Explainer Agent** teaches the concept clearly.
3. **Notes Agent** creates revision notes.
4. **Quiz Agent** generates assessment questions.
5. **Writer Agent** synthesizes everything into a polished student workbook.
6. **Feedback Agent** evaluates submitted answers and recommends next steps.
7. **SmartLearnManager** orchestrates the full pipeline and streams progress to the UI.

## Project structure

```text
smartlearn_multi_agent/
├── .env.example
├── README.md
├── requirements.txt
├── smartlearn_app.py
└── smartlearn/
    ├── __init__.py
    ├── config.py
    ├── manager.py
    ├── rendering.py
    ├── schemas.py
    ├── session_store.py
    ├── tools.py
    └── agents/
        ├── __init__.py
        ├── explainer_agent.py
        ├── feedback_agent.py
        ├── notes_agent.py
        ├── planner_agent.py
        ├── quiz_agent.py
        └── writer_agent.py
```

## Architecture choices

### 1. Deterministic orchestration manager

The original SmartLearn concept included a Coordinator Agent. In this implementation, a Python-based manager serves as the primary orchestrator.

This approach offers several advantages:

- Higher reliability for a fixed, structured learning workflow
- Simpler debugging and observability, especially in instructional settings
- Straightforward step-by-step progress streaming in the Gradio UI
- Preserves clear separation of concerns, with specialized agents handling each stage

### 2. Structured outputs everywhere

Each agent returns a Pydantic model. That makes downstream steps more robust.

Examples:
- lesson plan
- explanation pack
- notes pack
- quiz pack
- feedback pack

### 3. Optional grounded learning context

Users can paste lecture notes, textbook excerpts, or instructor material into the UI. SmartLearn extracts relevant snippets and uses them as grounding context.

This gives you a practical bridge toward future RAG/vector-store integration without forcing a full retrieval stack in version 1.

## Install

Create and activate a virtual environment, then install requirements.

### Using uv

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Using pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment variables

Copy `.env.example` to `.env` and set your API key.

```bash
cp .env.example .env
```

Minimum required:

```env
OPENAI_API_KEY=your_key_here
SMARTLEARN_MODEL=gpt-5.4-mini
```

## Run

```bash
python smartlearn_app.py
```

Then open the local Gradio URL in your browser.

## How to use

1. Enter a topic.
2. Select a learner level.
3. Optionally add a learning goal and prior knowledge.
4. Optionally paste course notes/reference text.
5. Click **Build Lesson**.
6. Review the generated workbook and quiz.
7. Paste answers using the answer template.
8. Click **Evaluate Answers**.

## Example ideas

- Explain recursion for beginners
- Teach gradient descent to intermediate learners
- Summarize photosynthesis for high-school revision
- Build a lesson on SQL joins using pasted lecture notes

## Future extensions

- vector store / true RAG over PDFs and lecture notes
- persistent learner profile
- spaced repetition scheduler
- adaptive quiz difficulty over time
- teacher dashboard
- LMS integration
- email/export of student workbook

## Notes on implementation


- Notes and quiz generation run in parallel using a thread pool after the explanation step.
- Evaluation uses both light deterministic auto-grading and an LLM feedback pass.
- Session state is stored in memory for demo simplicity.

