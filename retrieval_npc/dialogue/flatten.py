from typing import List, Dict

def flatten_dialogue_tree(nested_tree: List[Dict]) -> List[Dict]:
    flat_tree = []
    id_counter = [1]  # use a list to allow mutation in nested scope
    link_references = {}  # Store references to linked nodes

    def _flatten(node, parent_id=None):
        node_id = node.get("id")
        if not node_id:
            node_id = id_counter[0]
            id_counter[0] += 1

        flat_node = {k: v for k, v in node.items() if k not in ["children", "link_to"]}
        flat_node["id"] = node_id
        flat_node["parent_id"] = parent_id

        if "text" in flat_node and "tekst" not in flat_node:
            flat_node["tekst"] = flat_node["text"]

        # Removed conversion of requirements to conditions

        flat_tree.append(flat_node)

        if "link_to" in node:
            link_references[node_id] = node["link_to"]

        for child in node.get("children", []):
            _flatten(child, node_id)

    if not nested_tree:
        raise ValueError("Empty dialogue tree provided")

    for root in nested_tree:
        if root is None:
            continue
        _flatten(root)

    link_nodes = []
    for node_id, target_id in link_references.items():
        target_node = next((n for n in flat_tree if n["id"] == target_id), None)
        if target_node:
            linked_node = target_node.copy()
            linked_node["parent_id"] = node_id
            linked_node["id"] = f"{target_id}_linked_{node_id}"
            link_nodes.append(linked_node)

    flat_tree.extend(link_nodes)
    return flat_tree
