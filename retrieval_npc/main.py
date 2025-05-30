from dialogue.loader import load_dialogue_tree
from dialogue.flatten import flatten_dialogue_tree
from dialogue.dialogue_engine import run_dialogue

if __name__ == "__main__":
    nested_tree = load_dialogue_tree("data/conversation-tree.yaml")
    run_dialogue(nested_tree)
