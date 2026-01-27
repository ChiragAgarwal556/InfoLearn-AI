from checkpoints import CHECKPOINTS


def select_checkpoint(state):
    print("\n🎯 Available Learning Topics:\n")

    for cp in CHECKPOINTS:
        print(f"{cp['id']}. {cp['topic']}")

    while True:
        try:
            choice = int(input("\nEnter topic number to learn: "))
            if any(cp["id"] == choice for cp in CHECKPOINTS):
                break
            print("❌ Invalid choice. Try again.")
        except:
            print("❌ Enter a valid number.")

    print(f"\n✅ You selected: {choice}\n")

    return {"current_cp": choice}
