from llm_tools import llm, search_tool
from checkpoints import CHECKPOINTS


def select_checkpoint(state):
    print("\n📚 Available Topics:\n")

    for cp in CHECKPOINTS:
        print(f"{cp['id']}. {cp['topic']}")

    while True:
        try:
            choice = int(input("\nSelect topic number: "))
            checkpoint = next(c for c in CHECKPOINTS if c["id"] == choice)
            break
        except:
            print("❌ Invalid choice. Try again.")

    print(f"\n📘 CHECKPOINT {checkpoint['id']}: {checkpoint['topic']}")

    return {"checkpoint": checkpoint}


def explain_topic(state):
    checkpoint = state["checkpoint"]

    topic = checkpoint["topic"]
    objectives = checkpoint.get("objectives", [])

    print("\n📖 TOPIC EXPLANATION")
    print(f"Topic: {topic}")
    if objectives:
        print("Objectives:")
        for i, obj in enumerate(objectives, 1):
            print(f"  {i}. {obj}")
    print("-" * 60)

    query = f"Explain {topic} in simple terms with examples"
    web_text = search_tool.invoke(query)

    prompt = f"""
Explain the topic so that these objectives are achieved:
{objectives}

Use:
- simple words
- daily examples
- short paragraphs

TEXT:
{web_text}
"""

    notes = llm.invoke(prompt).content.strip()

    print(notes)
    print("-" * 60)

    return {"context": notes}
