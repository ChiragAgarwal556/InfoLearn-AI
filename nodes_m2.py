from llm_tools import llm
import json



# STEP 1: Generate MCQ Questions using LLM


def generate_questions(state):
    context = state.get("context", "")

    if not context:
        raise ValueError("❌ No learning context found. Explanation step failed.")

    prompt = f"""
Create exactly 5 MCQ questions from the study notes below.

STRICT RULES:
- Output ONLY valid JSON
- No explanation
- No extra text
- No markdown
- No numbering outside JSON

FORMAT:
[
  {{
    "question": "...",
    "options": {{"A":"", "B":"", "C":"", "D":""}},
    "answer": "A"
  }}
]

STUDY NOTES:
{context}
"""

    resp = llm.invoke(prompt).content.strip()

    try:
        mcqs = json.loads(resp)

        # basic validation
        if not isinstance(mcqs, list) or len(mcqs) != 5:
            raise ValueError("Invalid MCQ format")

        for q in mcqs:
            if (
                "question" not in q
                or "options" not in q
                or "answer" not in q
                or not all(k in q["options"] for k in ["A", "B", "C", "D"])
            ):
                raise ValueError("Invalid MCQ fields")

    except Exception:
        print("\n⚠ MCQ generation failed. Retrying...\n")
        return generate_questions(state)   # retry safely

    return {"questions": mcqs}


# -------------------------------------------------
# STEP 2: Ask MCQ Questions to Learner
# -------------------------------------------------

def ask_questions(state):
    questions = state.get("questions", [])

    if not questions:
        raise ValueError("❌ No MCQ questions available to ask.")

    answers = []

    print("\n📝 MCQ TEST (Choose A / B / C / D)")
    print("-" * 50)

    for i, q in enumerate(questions, start=1):
        print(f"\nQ{i}. {q['question']}")
        for k, v in q["options"].items():
            print(f"   {k}. {v}")

        while True:
            ans = input("Your answer: ").strip().upper()
            if ans in ["A", "B", "C", "D"]:
                break
            print("❌ Please enter A, B, C or D")

        answers.append(ans)

    return {"answers": answers}


# -------------------------------------------------
# STEP 3: Verify Answers & Score
# -------------------------------------------------

def verify_answers(state):
    questions = state.get("questions", [])
    answers = state.get("answers", [])
    checkpoint = state.get("checkpoint")

    if not questions or not answers:
        raise ValueError("❌ Missing questions or answers for evaluation.")

    correct = 0
    weak = []

    for i, q in enumerate(questions):
        if answers[i] == q["answer"]:
            correct += 1
        else:
            weak.append(q["question"])

    score = correct / len(questions)

    print("\n📊 MCQ RESULT")
    print(f"Correct: {correct}/{len(questions)}")
    print(f"Score: {int(score * 100)}%")

    if checkpoint and score >= checkpoint["success_threshold"]:
        print("✅ Status: PASSED")
    else:
        print("❌ Status: FAILED")

    return {"score": score, "weak_topics": weak}
