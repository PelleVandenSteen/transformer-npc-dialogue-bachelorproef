class GameState:
    def __init__(self):
        self.state = {
            "gold": 50,
            "has_entry_pass": False,
            "flags": [],
            "charisma": 15,
            "deception": 10,
            "intimidation": 10,
            "reputation": 20,
            "guard_hostility": 0,
            "guard_disposition": 0,
            "guard_suspicion": 0,
            "guard_corruption": 0,
            "entry_granted": False,
            "combat_initiated": False,
            "jarl_meeting_arranged": False,
            "job_opportunity": False
        }

    def get(self, key):
        return self.state.get(key, 0)  # Default to 0 for missing keys

    def set(self, key, value):
        self.state[key] = value

    def apply_changes(self, changes: dict):
        """Apply state changes from dialogue effects"""
        for key, value in changes.items():
            if isinstance(value, str) and value.startswith(('+', '-')):
                # Handle relative changes like "+2" or "-10"
                current_value = self.get(key)
                if value.startswith('+'):
                    new_value = current_value + int(value[1:])
                else:  # starts with '-'
                    new_value = current_value - int(value[1:])
                self.set(key, new_value)
            else:
                # Handle absolute values
                self.set(key, value)

    def meets_requirements(self, requirements: dict) -> bool:
        """Check if current state meets all requirements"""
        if not requirements:
            return True
        
        #print(f"[DEBUG] Checking requirements: {requirements}")
        #print(f"[DEBUG] Current state values: {self.state}")
            
        for key, required_value in requirements.items():
            if key.startswith('min_'):
                # Handle minimum requirements like "min_gold": 10
                stat_name = key[4:]  # Remove "min_" prefix
                current_value = self.get(stat_name)
                #print(f"[DEBUG] Checking {key}: need {required_value}, have {current_value}")
                if current_value < required_value:
                    #print(f"[DEBUG] Failed requirement: {key}")
                    return False
            elif key.startswith('max_'):
                # Handle maximum requirements like "max_hostility": 2
                stat_name = key[4:]  # Remove "max_" prefix
                current_value = self.get(stat_name)
                #print(f"[DEBUG] Checking {key}: max {required_value}, have {current_value}")
                if current_value > required_value:
                    #print(f"[DEBUG] Failed requirement: {key}")
                    return False
            else:
                # Handle exact matches
                current_value = self.get(key)
                #print(f"[DEBUG] Checking {key}: need {required_value}, have {current_value}")
                if current_value != required_value:
                    #print(f"[DEBUG] Failed requirement: {key}")
                    return False
                    
        #print(f"[DEBUG] All requirements met!")
        return True

    def __str__(self):
        """String representation for debugging"""
        relevant_stats = {k: v for k, v in self.state.items() if v != 0 or k in ['gold', 'entry_granted']}
        return f"GameState: {relevant_stats}"