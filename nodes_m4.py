from checkpoints import CHECKPOINTS


def next_checkpoint(state):
    current = state["checkpoint"]["id"]
    next_id = current + 1

    print(f"\n✅ Checkpoint {current} completed!")

    return {
        "current_cp": next_id,
        "context": "",
        "questions": [],
        "answers": [],
        "score": 0.0,
        "weak_topics": [],
    }


def course_complete(state):
    print("\n🎉 CONGRATULATIONS!")
    print("You have completed all selected learning topics.")
    print("Keep learning and growing 🚀\n")
    return {}
