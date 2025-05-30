import json
import yaml
import os
from dialogue.flatten import flatten_dialogue_tree

def load_dialogue_tree(path):
    _, ext = os.path.splitext(path)

    with open(path, "r", encoding="utf-8") as f:
        if ext.lower() in [".yaml", ".yml"]:
            data = yaml.safe_load(f)
            
            # Debug: Print what we loaded
            print(f"Loaded YAML data type: {type(data)}")
            if data is None:
                raise ValueError("YAML file appears to be empty or invalid")
            
            # Handle new nested conversation format
            if isinstance(data, dict) and "conversations" in data:
                # Extract all conversation trees and flatten them
                nested_tree = []
                for conversation_name, nodes in data["conversations"].items():
                    if isinstance(nodes, list):
                        nested_tree.extend(nodes)
                    else:
                        # Handle single node conversations
                        nested_tree.append(nodes)
                return flatten_dialogue_tree(nested_tree)
            elif isinstance(data, list):
                # Handle old format (direct list)
                return flatten_dialogue_tree(data)
            else:
                raise ValueError(f"Unexpected YAML structure. Expected dict with 'conversations' key or list, got: {type(data)}")
                
        elif ext.lower() == ".json":
            return json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {ext}")