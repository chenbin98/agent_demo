import os
from pathlib import Path
from pydantic_ai import Agent
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
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

# Load config from .env
load_env()
api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

if not api_key:
    raise RuntimeError("Missing DEEPSEEK_API_KEY in .env (or OPENAI_API_KEY).")

provider = OpenAIProvider(api_key=api_key, base_url=base_url)

# Build model with provider so key/base_url are honored
model = OpenAIModel("deepseek-chat", provider=provider)

agent = Agent(
    model,
    instructions=(
        "You are a MacOS script expert and interactive agent."
        "Always confirm before performing any destructive operations."
        "Your output should be concise, and each step should be clear and easy to follow."
    ),
    tools=[
        tools.create_text_file,
        tools.create_python_file,
        tools.get_directory_structure,
        tools.rename_file,
        tools.execute_windows_command,
        tools.get_host_info,
    ],
)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DeepSeek agent CLI")
    parser.add_argument("prompt", nargs="?", help="Prompt to send to the agent")
    parser.add_argument("--repl", action="store_true", help="Enter interactive REPL mode")
    args = parser.parse_args()

    if args.repl:
        print("Entering REPL. Press Ctrl+C to exit.")
        try:
            while True:
                try:
                    user_in = input(">>> ").strip()
                except EOFError:
                    break
                if not user_in:
                    continue
                result = agent.run_sync(user_in)
                print(result.output)
        except KeyboardInterrupt:
            print("\nBye")
    else:
        prompt = args.prompt or input("Enter prompt: ").strip()
        result = agent.run_sync(prompt)
        print(result.output)
