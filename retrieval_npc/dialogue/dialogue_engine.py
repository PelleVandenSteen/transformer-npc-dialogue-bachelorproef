import random
from dialogue.state import GameState


def get_children(tree, parent_id):
    return [node for node in tree if node["parent_id"] == parent_id]

def get_valid_npc_responses(tree, parent_id, state):
    options = [n for n in tree if n["parent_id"] == parent_id and n["speaker"].lower() in ["npc", "guard"]]
    valid = []

    for option in options:
        requirements = option.get("requirements")
        if requirements and not state.meets_requirements(requirements):
            continue

        valid.append(option)

    return valid

def get_valid_player_options(tree, parent_id, state):
    options = [n for n in tree if n["parent_id"] == parent_id and n["speaker"].lower() == "player"]
    valid = []

    for option in options:
        requirements = option.get("requirements")
        if requirements and not state.meets_requirements(requirements):
            continue

        valid.append(option)

    return valid

def apply_node_effects(node, state):
    effects = node.get("effects")
    if effects:
        state.apply_changes(effects)
        print(f"[Effects applied: {effects}]")

def check_end_state(node):
    end_state = node.get("end_state")
    if end_state:
        return True, end_state
    return False, None

def run_dialogue(tree, show_full_option_texts=False):
    state = GameState()
    #print(f"[DEBUG] Starting dialogue with state: {state}")

    start_node = None
    for node in tree:
        if node["id"] == "start" or node["parent_id"] is None:
            start_node = node
            break

    if not start_node:
        print("❌ No starting node found!")
        return

    current_node = start_node
    conversation_history = []

    while True:
        speaker_name = current_node["speaker"].title()
        dialogue_text = current_node.get("tekst", current_node.get("text", ""))
        mood = current_node.get("mood", "")

        if mood:
            print(f"\n{speaker_name} ({mood}): {dialogue_text}\n")
        else:
            print(f"\n{speaker_name}: {dialogue_text}\n")

        conversation_history.append((speaker_name, dialogue_text, mood))

        apply_node_effects(current_node, state)

        is_end, end_reason = check_end_state(current_node)
        if is_end:
            print(f"⚠️  Conversation ended: {end_reason}")
            print(f"Final state: {state}")
            break

        children = get_children(tree, current_node["id"])
        if not children:
            print("⚠️  End of conversation.")
            print(f"Final state: {state}")
            break

        if children and children[0]["speaker"].lower() in ["npc", "guard"]:
            valid_responses = get_valid_npc_responses(tree, current_node["id"], state)
            if not valid_responses:
                print("⚠️  No valid NPC responses available.")
                break

            current_node = random.choice(valid_responses)
            continue

        all_player_options = [n for n in children if n["speaker"].lower() == "player"]

        if not all_player_options:
            print("⚠️  No player options available.")
            break

        print("Choose your response:")
        #print(f"[DEBUG] Found {len(all_player_options)} player options")

        valid_options = []
        for idx, child in enumerate(all_player_options):
            requirements = child.get("requirements")
            if requirements and not state.meets_requirements(requirements):
                #print(f"[DEBUG] Option {idx+1} failed requirements: {requirements}")
                #print(f"[DEBUG] Current state: {dict(state.state)}")
                continue

            valid_options.append((len(valid_options) + 1, child))

        if not valid_options:
            print("⚠️  No valid player options meet requirements.")
            #print(f"[DEBUG] Current state: {state}")
            break

        for display_idx, child in valid_options:
            if show_full_option_texts:
                label = child.get("tekst", child.get("text", ""))
            else:
                label = child.get("description", child.get("tekst", child.get("text", "")))

            print(f"{display_idx}. {label}")

        try:
            choice = input("> ").strip()
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(valid_options):
                print("❌ Invalid choice. Please enter a number from the list.")
                continue

            chosen_option = valid_options[int(choice) - 1][1]
            current_node = chosen_option

        except (ValueError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

def print_conversation_summary(history):
    print("\n" + "="*50)
    print("CONVERSATION SUMMARY")
    print("="*50)
    for speaker, text, mood in history:
        mood_str = f" ({mood})" if mood else ""
        print(f"{speaker}{mood_str}: {text}")
