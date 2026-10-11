import streamlit as st
from agent import PlacementAgent, QUESTION_BANK, SUBJECTS, make_revision_plan

st.set_page_config(page_title="MechPrep | Placement Coach", page_icon="⚙️", layout="wide")
st.title("⚙️ MechPrep")
st.subheader("Agentic Mechanical Placement Coach")
st.write("An adaptive practice coach that identifies weak subjects, selects follow-up questions, and builds a revision plan.")

if "agent" not in st.session_state:
    st.session_state.agent = PlacementAgent()
if "current_q" not in st.session_state:
    st.session_state.current_q = None
if "answered_ids" not in st.session_state:
    st.session_state.answered_ids = []
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None
if "last_answer_correct" not in st.session_state:
    st.session_state.last_answer_correct = None

agent = st.session_state.agent

with st.sidebar:
    st.header("Your placement goal")
    target_role = st.selectbox("Target role", ["Mechanical Core", "Automotive", "Manufacturing / Quality", "Design / CAE"])
    available_days = st.slider("Days until assessment", 1, 30, 7)
    daily_minutes = st.slider("Study time per day (minutes)", 15, 180, 60, step=15)
    st.caption("Your settings are used to tailor the revision plan.")

tab1, tab2, tab3 = st.tabs(["🎯 Practice", "📊 Performance", "🗓️ Revision plan"])

with tab1:
    st.markdown("### Adaptive technical practice")
    st.write(f"Questions answered: **{len(agent.history)}**")
    if st.session_state.last_feedback:
        if st.session_state.last_answer_correct:
            st.success(st.session_state.last_feedback)
        else:
            st.warning(st.session_state.last_feedback)

    if st.session_state.current_q is None:
        if st.button("Start / choose next question", type="primary"):
            q = agent.choose_next_question(st.session_state.answered_ids)
            st.session_state.current_q = q
            st.rerun()
    else:
        q = st.session_state.current_q
        st.caption(f"Subject: {q['subject']} · Difficulty: {q['difficulty']}")
        st.markdown(f"**Question:** {q['question']}")
        selected = st.radio("Choose one answer", q["options"], key=f"answer_{q['id']}")
        if st.button("Submit answer", type="primary"):
            correct = selected == q["answer"]
            agent.record_answer(q, selected, correct)
            st.session_state.answered_ids.append(q["id"])
            st.session_state.last_answer_correct = correct
            st.session_state.last_feedback = (
                f"Correct! {q['explanation']}" if correct
                else f"Not quite. Correct answer: {q['answer']}. {q['explanation']}"
            )
            st.session_state.current_q = None
            st.rerun()

    if agent.history and st.button("Clear session and restart"):
        st.session_state.agent = PlacementAgent()
        st.session_state.current_q = None
        st.session_state.answered_ids = []
        st.session_state.last_feedback = None
        st.session_state.last_answer_correct = None
        st.rerun()

with tab2:
    st.markdown("### Your current skill profile")
    if not agent.history:
        st.info("Answer a few questions to see your skill profile.")
    else:
        scores = agent.subject_scores()
        cols = st.columns(2)
        for i, subject in enumerate(SUBJECTS):
            score = scores[subject]
            with cols[i % 2]:
                st.metric(subject, f"{score['percent']}%", f"{score['correct']}/{score['attempted']} correct")
                st.progress(score["percent"] / 100)
        weak = agent.weakest_subject()
        st.info(f"Agent decision: prioritize **{weak}** based on your current answers.")
        st.markdown("#### Recent answers")
        for entry in reversed(agent.history[-8:]):
            symbol = "✅" if entry["correct"] else "❌"
            st.write(f"{symbol} **{entry['subject']}** — {entry['question']}")

with tab3:
    st.markdown("### Personalized revision plan")
    if not agent.history:
        st.info("Answer at least one question first. The agent uses your results to prioritize the plan.")
    if st.button("Generate revision plan", type="primary"):
        plan = make_revision_plan(
            agent=agent, target_role=target_role,
            days=available_days, daily_minutes=daily_minutes
        )
        st.session_state.revision_plan = plan
    if "revision_plan" in st.session_state:
        for item in st.session_state.revision_plan:
            with st.container(border=True):
                st.markdown(f"**Day {item['day']}: {item['subject']}**")
                st.write(item["activity"])
                st.caption(f"Time: {item['minutes']} minutes · Reason: {item['reason']}")

st.divider()
st.caption("Prototype note: this is a transparent rule-based agent. It adapts its decisions using your answers; it does not use an external LLM.")
