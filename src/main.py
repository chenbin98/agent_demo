import os
import json
from pathlib import Path
from typing import List, Dict, Any
from pydantic_ai import Agent
from pydantic_ai.providers.openai import OpenAIProvider
# Prefer the newer Chat Completions model; fall back if unavailable
try:
    from pydantic_ai.models.openai import OpenAIChatModel
except Exception:  # pragma: no cover
    from pydantic_ai.models.openai import OpenAIModel as OpenAIChatModel
import tools

def load_env() -> None:
    """Load .env from common locations (cwd, script dir, parents)."""
    candidates: list[Path] = []
    cwd = Path.cwd()
    script_dir = Path(__file__).resolve().parent
    # Prefer closer files first
    candidates.extend([cwd / ".env", script_dir / ".env"])
    candidates.extend(p / ".env" for p in script_dir.parents)
    candidates.extend(p / ".env" for p in cwd.parents)

    loaded_any = False
    # Try python-dotenv first if available
    try:
        from dotenv import load_dotenv as _load

        for env_path in candidates:
            if env_path.is_file():
                _load(env_path)
                loaded_any = True
                break
    except Exception:
        pass

    if loaded_any:
        return

    # Fallback: simple parser
    for env_path in candidates:
        try:
            if not env_path.is_file():
                continue
            with env_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value
            break
        except Exception:
            continue

# Conversation history management
class ConversationHistory:
    """Manages conversation history for the LLM agent."""
    
    def __init__(self, history_file: str = "conversation_history.json"):
        self.history_file = Path(history_file)
        self.history: List[Dict[str, Any]] = []
        self.load_history()
    
    def load_history(self):
        """Load conversation history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                print(f"📚 Loaded {len(self.history)} previous conversations")
            else:
                print("📚 Starting fresh conversation history")
        except Exception as e:
            print(f"⚠️  Could not load conversation history: {e}")
            self.history = []
    
    def save_history(self):
        """Save conversation history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Could not save conversation history: {e}")
    
    def add_interaction(self, user_input: str, agent_response: str, timestamp: str = None):
        """Add a new interaction to the history."""
        if timestamp is None:
            from datetime import datetime
            timestamp = datetime.now().isoformat()
        
        interaction = {
            "timestamp": timestamp,
            "user_input": user_input,
            "agent_response": agent_response
        }
        self.history.append(interaction)
        self.save_history()
    
    def get_recent_context(self, max_interactions: int = 5) -> str:
        """Get recent conversation context for the LLM."""
        if not self.history:
            return ""
        
        recent = self.history[-max_interactions:]
        context_parts = []
        
        for i, interaction in enumerate(recent):
            context_parts.append(f"Previous interaction {i+1}:")
            context_parts.append(f"User: {interaction['user_input']}")
            context_parts.append(f"Agent: {interaction['agent_response']}")
            context_parts.append("---")
        
        return "\n".join(context_parts)
    
    def clear_history(self):
        """Clear all conversation history."""
        self.history = []
        self.save_history()
        print("🗑️  Conversation history cleared")
    
    def get_history_summary(self) -> str:
        """Get a summary of conversation history."""
        if not self.history:
            return "No previous conversations"
        
        total_interactions = len(self.history)
        recent_topics = []
        
        # Extract recent topics (last 3 interactions)
        for interaction in self.history[-3:]:
            user_input = interaction['user_input'].lower()
            if 'wheat' in user_input or 'yield' in user_input:
                recent_topics.append("Wheat yield prediction")
            elif 'file' in user_input or 'create' in user_input:
                recent_topics.append("File operations")
            elif 'system' in user_input or 'info' in user_input:
                recent_topics.append("System information")
            else:
                recent_topics.append("General assistance")
        
        return f"Total interactions: {total_interactions}, Recent topics: {', '.join(set(recent_topics))}"

# Initialize conversation history
conversation_history = ConversationHistory()

# Load config from .env
load_env()
api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

if not api_key:
    raise RuntimeError("Missing DEEPSEEK_API_KEY in .env (or OPENAI_API_KEY).")

provider = OpenAIProvider(api_key=api_key, base_url=base_url)

# Build model with provider so key/base_url are honored
model = OpenAIChatModel("deepseek-chat", provider=provider)

agent = Agent(
    model,
    instructions=(
        "You are a MacOS script expert and interactive agent with agricultural modeling capabilities."
        "Always confirm before performing any destructive operations."
        "Your output should be concise, and each step should be clear and easy to follow."
        "You can predict wheat yield using the AquaCrop model - this process is fully transparent to users."
        "\n\nIMPORTANT: You have access to conversation history. When users ask follow-up questions or refer to previous interactions, use the conversation context to provide more relevant and personalized responses. Reference previous wheat yield predictions, file operations, or system information when appropriate."
    ),
    tools=[
        tools.create_text_file,
        tools.create_python_file,
        tools.get_directory_structure,
        tools.rename_file,
        tools.execute_windows_command,
        tools.get_host_info,
        tools.predict_wheat_yield,
    ],
)

def create_agent():
    """Create and return the agent instance."""
    return agent

def run_agent_with_history(user_input: str) -> str:
    """Run the agent with conversation history context."""
    # Get recent conversation context
    context = conversation_history.get_recent_context()
    
    # Prepare the input with context
    if context:
        contextual_input = f"CONVERSATION HISTORY:\n{context}\n\nCURRENT REQUEST: {user_input}"
    else:
        contextual_input = user_input
    
    # Run the agent
    result = agent.run_sync(contextual_input)
    response = result.output
    
    # Add to conversation history
    conversation_history.add_interaction(user_input, response)
    
    return response

def get_conversation_summary() -> str:
    """Get a summary of the conversation history."""
    return conversation_history.get_history_summary()

def clear_conversation_history():
    """Clear the conversation history."""
    conversation_history.clear_history()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DeepSeek agent CLI with conversation history")
    parser.add_argument("prompt", nargs="*", help="Prompt to send to the agent (can be multiple words)")
    parser.add_argument("--repl", action="store_true", help="Enter interactive REPL mode")
    parser.add_argument("--clear-history", action="store_true", help="Clear conversation history")
    parser.add_argument("--history-summary", action="store_true", help="Show conversation history summary")
    args = parser.parse_args()

    # Handle special commands
    if args.clear_history:
        clear_conversation_history()
        exit(0)
    
    if args.history_summary:
        print(get_conversation_summary())
        exit(0)

    if args.repl:
        print("🤖 Entering REPL with conversation history. Press Ctrl+C to exit.")
        print("💡 Special commands: 'clear history', 'show history', 'help'")
        try:
            while True:
                try:
                    user_in = input(">>> ").strip()
                except EOFError:
                    break
                if not user_in:
                    continue
                
                # Handle special commands
                if user_in.lower() in ['clear history', 'clear']:
                    clear_conversation_history()
                    continue
                elif user_in.lower() in ['show history', 'history']:
                    print(get_conversation_summary())
                    continue
                elif user_in.lower() in ['help', '?']:
                    print("💡 Available commands:")
                    print("  - 'clear history' or 'clear': Clear conversation history")
                    print("  - 'show history' or 'history': Show conversation summary")
                    print("  - 'help' or '?': Show this help")
                    print("  - Any other text: Send to AI agent with conversation context")
                    continue
                
                # Run with history
                response = run_agent_with_history(user_in)
                print(response)
        except KeyboardInterrupt:
            print("\n👋 Bye! Conversation history saved.")
    else:
        if args.prompt:
            prompt = " ".join(args.prompt).strip()
        else:
            prompt = input("Enter prompt: ").strip()

        # Support positional command aliases (no leading dashes)
        normalized = prompt.lower()
        if normalized in {"clear-history", "clear history", "clear"}:
            clear_conversation_history()
            exit(0)
        if normalized in {"history-summary", "show history", "history"}:
            print(get_conversation_summary())
            exit(0)

        response = run_agent_with_history(prompt)
        print(response)
