# MechPrep — Agentic Mechanical Placement Coach

## Project summary
MechPrep is an educational agentic AI prototype for mechanical engineering placement preparation. It quizzes students across five core subjects, tracks their performance, identifies weaker areas, chooses follow-up questions, and generates a revision plan.

## Agent cycle
**Assess → Diagnose → Decide → Act → Evaluate → Adapt**

## Features
- Interactive multiple-choice technical questions
- Five mechanical engineering subject areas
- Subject-wise score tracking
- Adaptive follow-up question selection
- Explanations after each answer
- Role-aware revision recommendations
- No API key or paid service required

## Technology
- Python
- Streamlit
- In-memory session state

## Run locally
Install Python 3.10 or later, then open a terminal in this project folder:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

A local browser tab will open with the application.

## Demo script
1. Start the app and answer a question incorrectly.
2. Notice the explanation and feedback.
3. Answer more questions in different subjects.
4. Open Performance to see subject-wise scores and the agent's weak-area decision.
5. Generate a revision plan.
6. Explain that new answers update the profile and influence later question selection.

## Agent architecture
See `schema.md` for the architecture diagram, input schema, decision policy, PEAS description and test cases.

## Honest limitation
This is a transparent rule-based agent prototype rather than a large language model. Its adaptive behaviour comes from its decision policy and session feedback.
