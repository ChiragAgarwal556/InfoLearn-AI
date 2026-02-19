import streamlit as st
from llm_tools import llm
import json
import sqlite3

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="InfoLearn AI | Infosys Learning Agent",
    page_icon="🎓",
    layout="centered"
)

# =============================
# PROFESSIONAL CSS STYLING
# =============================
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #eef2f7, #f9fbfd);
    font-family: 'Segoe UI', sans-serif;
}

/* Main Card */
.block-container {
    background: white;
    padding: 2rem 3rem 3rem 3rem;
    border-radius: 20px;
    box-shadow: 0px 10px 40px rgba(0,0,0,0.08);
}

/* Headings */
h1, h2, h3 {
    font-weight: 700;
    color: #111827;
}

h1 { font-size: 32px; }
h2 { font-size: 24px; }
h3 { font-size: 20px; }

/* Buttons */
.stButton > button {
    border-radius: 12px;
    background: linear-gradient(135deg, #2563eb, #4f46e5);
    color: white;
    border: none;
    padding: 0.6rem 1.3rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0px 8px 20px rgba(79,70,229,0.4);
}

/* Selectbox */
div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border: 1px solid #d1d5db !important;
}

div[data-baseweb="select"] > div:hover {
    border-color: #4f46e5 !important;
}

/* Radio */
.stRadio > div {
    background-color: #f3f4f6;
    padding: 10px;
    border-radius: 12px;
}

/* Metric */
[data-testid="stMetricValue"] {
    font-size: 32px;
    font-weight: bold;
    color: #2563eb;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #111827;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: #1f2937;
    border-radius: 10px;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #2563eb;
}

/* Divider */
hr {
    border: 0;
    height: 1px;
    background: #e5e7eb;
    margin: 1.5rem 0;
}

</style>
""", unsafe_allow_html=True)

# =============================
# DATABASE SETUP
# =============================
conn = sqlite3.connect("infolearn.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    checkpoint TEXT,
    score REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()
conn.close()

# =============================
# LOGIN PAGE
# =============================
def login_page():
    st.markdown("<h1 style='text-align:center;'>🎓 InfoLearn AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:gray;'>Infosys Intelligent Adaptive Learning System</p>", unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            conn = sqlite3.connect("infolearn.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "learn"
                st.rerun()
            else:
                st.error("Invalid username or password ❌")

    with tab2:
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password", type="password", key="reg_pass")

        if st.button("Register"):
            conn = sqlite3.connect("infolearn.db")
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_user, new_pass))
                conn.commit()
                conn.close()
                st.success("Account created successfully! Please login.")
            except sqlite3.IntegrityError:
                st.error("Username already exists ❌")
                conn.close()

# =============================
# SESSION DEFAULTS
# =============================
defaults = {
    "logged_in": False,
    "username": "",
    "show_results": False,
    "show_profile": False,
    "latest_score": None,
    "page": "learn",
    "context": "",
    "questions": [],
    "prev_questions": set(),
    "weak_areas": [],
    "retest_mode": False,
    "selected_checkpoint": None,
    "current_threshold": 0.6
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state.logged_in:
    login_page()
    st.stop()

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.markdown("## ☰ Menu")
    st.markdown(f"👤 **{st.session_state.username}**")
    st.divider()

    if st.button("📊 Results"):
        st.session_state.show_results = True
        st.session_state.show_profile = False

    if st.button("👤 User Account"):
        st.session_state.show_profile = True
        st.session_state.show_results = False

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# =============================
# PROFILE PAGE
# =============================
if st.session_state.show_profile:
    st.title("👤 User Profile")
    st.write("Username:", st.session_state.username)
    st.write("Role: Learner")

    st.divider()

    if st.button("🏠 Back to Main Menu"):
        st.session_state.show_profile = False
        st.rerun()

    st.stop()

# =============================
# RESULTS PAGE
# =============================
if st.session_state.show_results:
    st.title("📊 Results")

    conn = sqlite3.connect("infolearn.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT checkpoint, score FROM results
    WHERE username = ?
    ORDER BY id DESC
    """, (st.session_state.username,))
    history_rows = cursor.fetchall()

    cursor.execute("""
    SELECT checkpoint, COUNT(*), MAX(score), AVG(score)
    FROM results
    WHERE username = ?
    GROUP BY checkpoint
    """, (st.session_state.username,))
    progress_rows = cursor.fetchall()

    conn.close()

    if history_rows:
        st.subheader("📈 Test History")
        for row in history_rows:
            st.write(f"**{row[0]}** → {int(row[1]*100)}%")

        st.divider()
        st.subheader("📊 Progress Tracking Per Checkpoint")

        for row in progress_rows:
            mastery_status = "✅ Mastered" if row[2] >= 0.6 else "❌ Not Mastered"
            st.markdown(f"### 📘 {row[0]}")
            st.write(f"Attempts: {row[1]}")
            st.write(f"Best Score: {int(row[2]*100)}%")
            st.write(f"Average Score: {int(row[3]*100)}%")
            st.write(f"Status: {mastery_status}")
            st.markdown("---")
    else:
        st.info("No test attempts yet.")

    if st.button("🏠 Back to Main Menu"):
        st.session_state.show_results = False
        st.rerun()

    st.stop()

# =============================
# CHECKPOINTS
# =============================
CHECKPOINTS = [
    {"id":1,"topic":"Introduction to Machine Learning","objectives":["What is ML","Why ML is useful","Daily life examples"],"success_threshold":0.6},
    {"id":2,"topic":"Types of Machine Learning","objectives":["Supervised Learning","Unsupervised Learning","Reinforcement Learning"],"success_threshold":0.6},
    {"id":3,"topic":"Training vs Testing Data","objectives":["Data split","Overfitting","Evaluation methods"],"success_threshold":0.6},
    {"id":4,"topic":"Supervised Learning Algorithms","objectives":["Linear Regression","Logistic Regression","KNN basics"],"success_threshold":0.6},
    {"id":5,"topic":"Unsupervised Learning Algorithms","objectives":["Clustering","K-Means","Dimensionality Reduction"],"success_threshold":0.6},
    {"id":6,"topic":"Model Evaluation Metrics","objectives":["Accuracy","Precision & Recall","Confusion Matrix"],"success_threshold":0.6},
    {"id":7,"topic":"Overfitting and Underfitting","objectives":["Bias vs Variance","Model complexity","Cross validation"],"success_threshold":0.6},
    {"id":8,"topic":"Feature Engineering","objectives":["Feature selection","Feature scaling","Encoding categorical data"],"success_threshold":0.6},
    {"id":9,"topic":"Neural Networks Basics","objectives":["Perceptron","Activation functions","Hidden layers"],"success_threshold":0.6},
    {"id":10,"topic":"Real World ML Applications","objectives":["Recommendation systems","Fraud detection","Healthcare AI"],"success_threshold":0.6},
]

# =============================
# SAFE JSON PARSER
# =============================
def safe_json_parse(response):
    response = response.strip()

    # Remove markdown code blocks
    if "```" in response:
        response = response.split("```")[1]

    # Try to extract JSON array from messy output
    start = response.find("[")
    end = response.rfind("]")

    if start != -1 and end != -1:
        response = response[start:end+1]

    try:
        data = json.loads(response)

        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    return []
                if "question" not in item or "options" not in item or "answer" not in item:
                    return []
            return data

        return []

    except Exception as e:
        return []


# =============================
# MCQ GENERATORS
# =============================
def generate_mcqs_from_notes(notes, banned):
    prompt = f"""
Create 5 scenario based MCQs.

Return ONLY valid JSON.
No explanation.
No markdown.
No text outside JSON.

Format:
[
  {{
    "question": "...",
    "options": {{"A":"", "B":"", "C":"", "D":""}},
    "answer": "A"
  }}
]

Do NOT repeat:
{list(banned)}

Notes:
{notes}
"""
    response = llm.invoke(prompt).content
    return safe_json_parse(response)

def generate_mcqs_from_weak(weak, banned):
    if not weak:
        weak = ["Concept revision"]

    prompt = f"""
Student answered these incorrectly:
{weak}

Create 5 NEW scenario-based MCQs focusing only on these weak areas.

Avoid repeating these previous questions:
{list(banned)}

Return ONLY valid JSON.
No explanation.
No markdown.
No text outside JSON.

Strict format:
[
  {{
    "question": "Question text",
    "options": {{
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D"
    }},
    "answer": "A"
  }}
]
"""
    response = llm.invoke(prompt).content
    return safe_json_parse(response)

# =============================
# LEARN PAGE
# =============================
if st.session_state.page == "learn":

    st.title("🎓 InfoLearn AI")
    st.write("### Infosys Intelligent Adaptive Learning System")
    st.divider()

    st.subheader("📚 Select Topic")
    topic_names = [f"{c['id']}. {c['topic']}" for c in CHECKPOINTS]
    choice = st.selectbox("Choose a checkpoint:", topic_names)

    checkpoint = CHECKPOINTS[int(choice.split(".")[0]) - 1]
    st.session_state.selected_checkpoint = checkpoint

    if st.button("Start Learning"):
        objectives = "\n".join(checkpoint["objectives"])
        prompt = f"""
Explain {checkpoint['topic']} simply.
Objectives:
{objectives}
Use simple English and real life examples.
"""
        with st.spinner("Teaching..."):
            notes = llm.invoke(prompt).content

        st.session_state.context = notes
        st.session_state.retest_mode = False

    if st.session_state.context:
        st.subheader("📘 Explanation")
        st.write(st.session_state.context)

        if st.button("📝 Take Test"):
            st.session_state.current_threshold = checkpoint["success_threshold"]
            st.session_state.page = "test"
            st.session_state.questions = []
            st.rerun()

# =============================
# TEST PAGE
# =============================
if st.session_state.page == "test":

    if not st.session_state.questions:
        with st.spinner("Generating Questions..."):
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

        if not mcqs:
            st.error("⚠ Question generation failed. Try again.")
            st.stop()

        st.session_state.questions = mcqs

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

    if submit:
        correct = 0
        weak = []

        for i, q in enumerate(st.session_state.questions):
            if user_answers[i] == q["answer"]:
                correct += 1
            else:
                weak.append(q["question"])

        score = correct / len(st.session_state.questions)

        st.session_state.latest_score = score
        st.session_state.weak_areas = weak
        st.session_state.prev_questions.update(
            [q["question"] for q in st.session_state.questions]
        )

        conn = sqlite3.connect("infolearn.db")
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO results (username, checkpoint, score)
        VALUES (?, ?, ?)
        """, (
            st.session_state.username,
            st.session_state.selected_checkpoint["topic"],
            score
        ))
        conn.commit()
        conn.close()

        st.session_state.page = "result"
        st.rerun()

# =============================
# RESULT PAGE
# =============================
if st.session_state.page == "result":

    st.subheader("📊 Performance Report")

    score = st.session_state.latest_score
    threshold = st.session_state.current_threshold

    st.metric("Score", f"{int(score * 100)}%")

    if score >= threshold:
        st.success("🎉 Congratulations! Topic mastered.")

        if st.button("🔙 Back to Learning"):
            st.session_state.page = "learn"
            st.session_state.questions = []
            st.session_state.weak_areas = []
            st.session_state.retest_mode = False
            st.session_state.context = ""
            st.rerun()
    else:
        st.warning("⚠ Needs improvement. Re-teaching weak areas.")

        prompt = f"""
Student misunderstood:
{st.session_state.weak_areas}

Re-teach using simple language and daily life examples.
"""
        teach = llm.invoke(prompt).content

        st.subheader("🧠 Feynman Re-Teaching")
        st.write(teach)

        if st.button("🔁 Retest Weak Areas"):
            st.session_state.retest_mode = True
            st.session_state.questions = []
            st.session_state.page = "test"
            st.rerun()
