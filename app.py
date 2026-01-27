import streamlit as st
from llm_tools import llm
import json


st.set_page_config(
    page_title="InfoLearn AI | Infosys Learning Agent",
    page_icon="🎓",
    layout="centered"
)

st.markdown("""
<style>
body {background-color: #f5f7fb;}
.main {background-color: #f5f7fb;}
.card {
    background-color: white;
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 22px;
}
.title-text {
    color: #0033a0;
    font-size: 36px;
    font-weight: 700;
}
.sub-text {
    color: #444;
    font-size: 16px;
}
.section-title {
    color: #0033a0;
    font-weight: 600;
}
.stButton>button {
    background-color: #0033a0;
    color: white;
    border-radius: 8px;
    padding: 8px 22px;
    font-weight: 600;
}
.stButton>button:hover {
    background-color: #001f66;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# TITLE


st.markdown('<div class="title-text">🎓 InfoLearn AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Autonomous Learning Agent using Feynman Technique</div>', unsafe_allow_html=True)
st.markdown("---")

 
# CHECKPOINTS
 

CHECKPOINTS = [
    {"id":1,"topic":"Introduction to Machine Learning","objectives":["What is ML","Why ML is useful","Daily life examples"],"success_threshold":0.6},
    {"id":2,"topic":"Types of Machine Learning","objectives":["Supervised learning","Unsupervised learning","Reinforcement learning"],"success_threshold":0.6},
    {"id":3,"topic":"Training vs Testing Data","objectives":["Why data is split","Overfitting risk","Model evaluation"],"success_threshold":0.6},
    {"id":4,"topic":"Overfitting & Underfitting","objectives":["Bias vs variance","Model complexity","Generalization"],"success_threshold":0.6},
    {"id":5,"topic":"Regression vs Classification","objectives":["Continuous output","Categorical output","Examples"],"success_threshold":0.6},
]

 
# SESSION STATE
 

for k, v in {
    "context": "",
    "questions": [],
    "show_test": False,
    "prev_questions": set(),
    "weak_areas": [],
    "retest_mode": False
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

 
# TOPIC SELECTION
 

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📚 Select Learning Topic")

topic_names = [f"{c['id']}. {c['topic']}" for c in CHECKPOINTS]
choice = st.selectbox("Choose a checkpoint:", topic_names)

checkpoint = CHECKPOINTS[int(choice.split(".")[0]) - 1]
st.markdown('</div>', unsafe_allow_html=True)

 
# LEARNING PHASE
 

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📖 Learning Phase")

if st.button("Start Learning"):
    obj_text = "\n".join(checkpoint["objectives"])

    prompt = f"""
Explain {checkpoint['topic']} in very simple words.

Objectives:
{obj_text}

Rules:
- Simple English
- Daily life examples
- No MCQs
- No questions
"""

    with st.spinner("Teaching in progress..."):
        notes = llm.invoke(prompt).content

    st.session_state.context = notes
    st.session_state.questions = []
    st.session_state.show_test = False
    st.session_state.prev_questions = set()
    st.session_state.retest_mode = False

st.markdown('</div>', unsafe_allow_html=True)

 
# SHOW EXPLANATION
 

if st.session_state.context:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📘 Explanation")
    st.write(st.session_state.context)
    st.markdown('</div>', unsafe_allow_html=True)

 
# START TEST
 

if st.session_state.context and st.button("📝 Take Test"):
    st.session_state.show_test = True
    st.session_state.questions = []

 
# MCQ GENERATORS
 

def generate_mcqs_from_notes(notes, banned):
    prompt = f"""
Create 5 scenario based MCQs from the notes.

Rules:
- No theory definitions
- Real life situations
- Do NOT repeat:
{list(banned)}

Return ONLY valid JSON:
[
  {{
    "question": "...",
    "options": {{"A":"", "B":"", "C":"", "D":""}},
    "answer": "A"
  }}
]

NOTES:
{notes}
"""
    return json.loads(llm.invoke(prompt).content)


def generate_mcqs_from_weak(weak_points, banned):
    prompt = f"""
Student failed these topics:
{weak_points}

Create 5 new MCQs only from these.

Rules:
- Scenario based
- Different meaning
- Do NOT repeat:
{list(banned)}

Return ONLY JSON.
"""
    return json.loads(llm.invoke(prompt).content)

 
# GENERATE QUESTIONS
 

if st.session_state.show_test and not st.session_state.questions:
    with st.spinner("Generating questions..."):
        if st.session_state.retest_mode:
            mcqs = generate_mcqs_from_weak(
                st.session_state.weak_areas,
                st.session_state.prev_questions
            )
        else:
            mcqs = generate_mcqs_from_notes(
                st.session_state.context,
                st.session_state.prev_questions
            )
    st.session_state.questions = mcqs

 
# MCQ FORM
 

if st.session_state.show_test and st.session_state.questions:

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Knowledge Check")

    user_answers = []

    with st.form("mcq_form"):
        for i, q in enumerate(st.session_state.questions):
            st.write(f"**Q{i+1}. {q['question']}**")
            ans = st.radio(
                "Choose:",
                ["A", "B", "C", "D"],
                format_func=lambda x: f"{x}. {q['options'][x]}",
                key=f"q{i}"
            )
            user_answers.append(ans)

        submit = st.form_submit_button("Submit Answers")

    st.markdown('</div>', unsafe_allow_html=True)

    
    # RESULT + FEYNMAN RE-TEACHING
    

    if submit:
        correct = 0
        weak = []

        for i, q in enumerate(st.session_state.questions):
            if user_answers[i] == q["answer"]:
                correct += 1
            else:
                weak.append(q["question"])

        score = correct / len(st.session_state.questions)

        for q in st.session_state.questions:
            st.session_state.prev_questions.add(q["question"])

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Performance Report")
        st.metric("Score", f"{int(score*100)}%")

        if score >= checkpoint["success_threshold"]:
            st.success("🎉 Congratulations! Topic mastered.")
            st.session_state.show_test = False
            st.session_state.retest_mode = False

        else:
            st.warning("⚠ Needs improvement. Re-teaching weak areas.")

            prompt = f"""
Student misunderstood:
{weak}

Re-teach ONLY these parts using:
- simple language
- daily life examples
"""

            with st.spinner("Re-teaching weak areas..."):
                teach = llm.invoke(prompt).content

            st.subheader("🧠 Feynman Re-Teaching")
            st.write(teach)

            st.session_state.weak_areas = weak
            st.session_state.retest_mode = True

            if st.button("🔁 Retest Weak Areas"):
                st.session_state.questions = []
                st.session_state.show_test = True

        st.markdown('</div>', unsafe_allow_html=True)
