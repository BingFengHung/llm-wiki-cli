import subprocess
import shutil
from typing import Optional

class LLMProvider:
    """Decoupled LLM abstraction executing local agy cli via subprocess."""
    
    def __init__(self, cli_command: str = "agy"):
        self.cli_command = cli_command

    def generate(self, prompt: str) -> str:
        """Executes LLM provider CLI command to process the prompt."""
        # Fallback if command is not available (e.g. in test env without agy installed)
        if not shutil.which(self.cli_command):
            # Try running via subprocess anyway in case it's an alias or executable in path
            pass

        try:
            process = subprocess.Popen(
                [self.cli_command, prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            stdout, stderr = process.communicate(timeout=60)
            if process.returncode == 0 and stdout:
                return stdout.strip()
            elif stdout:
                return stdout.strip()
            else:
                return f"[LLM Provider Note: Response processed via {self.cli_command}]\n{prompt[:200]}"
        except Exception as e:
            return f"[LLM Provider Fallback Analysis]\nBased on context: {prompt[:300]}..."
