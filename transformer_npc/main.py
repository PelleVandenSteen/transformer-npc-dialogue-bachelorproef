import yaml
import requests
import time
import json

class NPCConversationSystem:
    def __init__(self, tree_file="claude's-tree-of-madness.yaml"):
        self.tree = self.load_tree(tree_file)
        self.current_node = self.tree[0]  # Start at the first node
        self.context = []
        self.game_state = {
            'guard_hostility': 0,
            'guard_disposition': 0,
            'guard_suspicion': 0,
            'reputation': 0,
        }
    
    def load_tree(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            tree = yaml.safe_load(file)
        return tree['conversations']['guard_initial_encounter']
    
    def ask_ollama(self, prompt):
        url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,  # Higher creativity for varied responses
                "num_predict": 80,   # Keep responses concise
                "top_p": 0.9
            }
        }

        try:
            start = time.time()
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            end = time.time()

            if response.status_code == 200:
                result = response.json()
                reply = result["response"].strip()
                return reply, end - start
            else:
                print(f"[ERROR] {response.status_code}: {response.text}")
                return None, 0
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            return None, 0
    
    def apply_effects(self, effects):
        """Apply node effects to game state"""
        if not effects:
            return
        
        for key, value in effects.items():
            if key in self.game_state:
                if isinstance(value, str) and value.startswith('+'):
                    self.game_state[key] += int(value[1:])
                elif isinstance(value, str) and value.startswith('-'):
                    self.game_state[key] -= int(value[1:])
                else:
                    self.game_state[key] = value
    
    def check_requirements(self, requirements):
        """Check if player meets requirements for a choice"""
        if not requirements:
            return True
        
        for req, value in requirements.items():
            if req == 'min_gold' and self.game_state['gold'] < value:
                return False
            elif req == 'min_intimidation':
                # Placeholder - you'd implement actual skill checks
                return True
            elif req == 'min_deception':
                return True
            elif req == 'min_charisma':
                return True
        
        return True
    
    def get_available_choices(self):
        """Get player choices that meet requirements"""
        if not self.current_node.get('children'):
            return []
        
        choices = []
        for child in self.current_node['children']:
            if child['speaker'] == 'player':
                if self.check_requirements(child.get('requirements')):
                    choices.append(child)
        
        return choices
    
    def get_guard_personality_context(self):
        """Build personality context based on current game state"""
        personality = []
        
        if self.game_state['guard_hostility'] >= 3:
            personality.append("very angry and aggressive")
        elif self.game_state['guard_hostility'] >= 1:
            personality.append("irritated and stern")
        
        if self.game_state['guard_disposition'] >= 2:
            personality.append("friendly and helpful")
        elif self.game_state['guard_disposition'] >= 1:
            personality.append("warming up to the conversation")
        elif self.game_state['guard_disposition'] <= -1:
            personality.append("cold and dismissive")
        
        if self.game_state['guard_suspicion'] >= 3:
            personality.append("very suspicious and watchful")
        elif self.game_state['guard_suspicion'] >= 1:
            personality.append("somewhat suspicious")
        
        if not personality:
            personality.append("professional but neutral")
        
        return ", ".join(personality)
    
    def enhance_npc_response(self, scripted_text, mood=None):
        """Use AI to add personality and variation to scripted responses"""
        
        # Build context about the guard's current state
        personality_context = self.get_guard_personality_context()
        mood_text = f" The guard is {mood}." if mood else ""
        
        # Get recent conversation context
        recent_context = ""
        if len(self.context) > 0:
            recent_context = f"\n\nRecent conversation:\n" + "\n".join(self.context[-4:])
        
        prompt = f"""You are a medieval city guard at the gates. You are currently {personality_context}.{mood_text}

Your scripted response is: "{scripted_text}"

Rewrite this response to sound more natural and expressive while:
- Keeping the exact same meaning and information
- Staying true to your current personality state
- Making it sound like natural spoken dialogue
- Being concise (1-2 sentences maximum)
- Not adding new information or changing the story{recent_context}
- But always change the scripted response in some way
Enhanced response:"""
        
        enhanced_response, duration = self.ask_ollama(prompt)
        
        # Fallback to original if AI fails or returns something inappropriate
        if not enhanced_response or "Error" in enhanced_response:
            return scripted_text
        
        # Basic sanity check - if response is way too long or short, use original
        if len(enhanced_response) > len(scripted_text) * 2 or len(enhanced_response) < len(scripted_text) * 0.3:
            return scripted_text
        
        return enhanced_response
    
    def show_choices(self, choices):
        """Display available choices to player"""
        if not choices:
            print("\n[No available responses - conversation may be ending]")
            return
        
        print("\nYour options:")
        for i, choice in enumerate(choices):
            # Show description if available (like "Attempt Bribe (-10 gold)")
            desc = choice.get('description', '')
            desc_text = f" [{desc}]" if desc else ""
            
            # Check if choice has requirements that aren't met (for display purposes)
            req_text = ""
            requirements = choice.get('requirements', {})
            if 'min_gold' in requirements:
                req_text = f" (Requires {requirements['min_gold']} gold)"
            
            print(f"{i + 1}. {choice['text']}{desc_text}{req_text}")
    
    def find_npc_response_node(self, player_choice):
        """Find the NPC's response to the player's choice"""
        if not player_choice.get('children'):
            return None
        
        # Look for guard responses in the children
        for child in player_choice['children']:
            if child['speaker'] == 'guard':
                return child
        
        return None
    
    def run_conversation(self):
        """Main conversation loop"""
        print("=== Medieval City Gate ===")
        
        # Start with the initial NPC line (enhanced)
        initial_response = self.enhance_npc_response(
            self.current_node['text'], 
            self.current_node.get('mood')
        )
        print(f"\nGuard: {initial_response}")
        self.context.append(f"Guard: {initial_response}")
        
        while True:
            choices = self.get_available_choices()
            
            if not choices:
                print("\n[Conversation has ended]")
                break
            
            self.show_choices(choices)
            
            # Get player choice
            try:
                choice_input = input(f"\nChoose your response (1-{len(choices)}): ").strip()
                choice_idx = int(choice_input) - 1
                
                if choice_idx < 0 or choice_idx >= len(choices):
                    print("Invalid choice. Please try again.")
                    continue
                    
                selected_choice = choices[choice_idx]
                
            except (ValueError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            
            # Show player's choice
            player_text = selected_choice['text']
            print(f"\nYou: {player_text}")
            self.context.append(f"Player: {player_text}")
            
            # Apply any effects from the player's choice
            self.apply_effects(selected_choice.get('effects'))
            
            # Find the NPC's scripted response
            npc_response_node = self.find_npc_response_node(selected_choice)
            
            if npc_response_node:
                # Enhance the scripted response with AI
                enhanced_response = self.enhance_npc_response(
                    npc_response_node['text'],
                    npc_response_node.get('mood')
                )
                
                print(f"\nGuard: {enhanced_response}")
                self.context.append(f"Guard: {enhanced_response}")
                
                # Update current node for next iteration
                self.current_node = npc_response_node
                
                # Check for conversation end
                if npc_response_node.get('end_state'):
                    end_state = npc_response_node['end_state']
                    print(f"\n=== {end_state.replace('_', ' ').title()} ===")
                    break
                    
                # Show debug info if game state changed significantly
                if any(abs(self.game_state[key]) > 1 for key in ['guard_hostility', 'guard_disposition', 'guard_suspicion']):
                    print(f"\n[Guard seems {self.get_guard_personality_context()}]")
            
            else:
                print("\n[No scripted response found - conversation ending]")
                break

def main():
    print("Starting NPC Conversation System...")
    print("Make sure Ollama is running with Mistral loaded!")
    
    try:
        system = NPCConversationSystem()
        system.run_conversation()
        
    except FileNotFoundError:
        print("Error: conversation-tree.yaml not found in current directory!")
    except KeyboardInterrupt:
        print("\n\nConversation interrupted.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
