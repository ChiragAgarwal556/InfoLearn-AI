from llm_tools import llm


def feynman_teach(state):
    prompt = f"""
Student answered these questions incorrectly:
{state['weak_topics']}

Explain using:
- very easy words
- daily life examples
- no technical terms
"""
    explanation = llm.invoke(prompt).content

    print("\n🧠 FEYNMAN RE-TEACHING")
    print("-" * 60)
    print(explanation)
    print("-" * 60)

    # IMPORTANT: clear old questions
    state["questions"] = []
    state["answers"] = []
    return state

