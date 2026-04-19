import json
import os
import logging
from typing import Any, Dict, List, Optional

from file_tools import read_file, list_files, write_file, search_in_file, TOOLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentAssistant:
    def __init__(self, llm_provider: str = "openai", api_key: str = None, model: str = None):
        self.provider = llm_provider.lower()
        self.model = model
        self.client = None
        self.messages = []

        if self.provider == "openai":
            self._setup_openai(api_key, model)
        elif self.provider == "anthropic":
            self._setup_anthropic(api_key, model)
        else:
            raise ValueError(f"Provider must be openai or anthropic, got {self.provider}")

    def _setup_openai(self, key: str, model: str):
        try:
            import openai
            key = key or os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError("OPENAI_API_KEY required")
            self.client = openai.OpenAI(api_key=key)
            self.model = model or "gpt-4-turbo-preview"
            logger.info(f"OpenAI ready: {self.model}")
        except ImportError:
            raise ImportError("openai library required")

    def _setup_anthropic(self, key: str, model: str):
        try:
            import anthropic
            key = key or os.getenv("ANTHROPIC_API_KEY")
            if not key:
                raise ValueError("ANTHROPIC_API_KEY required")
            self.client = anthropic.Anthropic(api_key=key)
            self.model = model or "claude-3-sonnet-20240229"
            logger.info(f"Anthropic ready: {self.model}")
        except ImportError:
            raise ImportError("anthropic library required")

    def ask(self, question: str, max_loops: int = 10) -> Dict[str, Any]:
        try:
            logger.info(f"Question: {question}")

            self.messages.append({"role": "user", "content": question})

            tools_called = []
            loop = 0

            while loop < max_loops:
                loop += 1

                if self.provider == "openai":
                    resp = self.client.chat.completions.create(
                        model=self.model,
                        messages=self.messages,
                        tools=[{"type": "function", "function": t} for t in TOOLS],
                        tool_choice="auto",
                        temperature=0.7
                    )
                else:
                    resp = self.client.messages.create(
                        model=self.model,
                        max_tokens=4096,
                        tools=[{"name": t["name"], "description": t["description"], "input_schema": t["input_schema"]} for t in TOOLS],
                        messages=self.messages
                    )

                if self.provider == "openai":
                    if not resp.choices[0].message.tool_calls:
                        final = resp.choices[0].message.content or ""
                        return {"success": True, "answer": final, "tools": tools_called}

                    self.messages.append({"role": "assistant", "content": resp.choices[0].message.content or "", "tool_calls": resp.choices[0].message.tool_calls})

                    for tc in resp.choices[0].message.tool_calls:
                        tool_result = self._run_tool(tc.function.name, json.loads(tc.function.arguments))
                        tools_called.append({"tool": tc.function.name, "result": tool_result})
                        self.messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(tool_result)})
                else:
                    has_tools = any(b.type == "tool_use" for b in resp.content)
                    if not has_tools:
                        final = "".join(b.text for b in resp.content if hasattr(b, "text"))
                        return {"success": True, "answer": final, "tools": tools_called}

                    for block in resp.content:
                        if block.type == "tool_use":
                            tool_result = self._run_tool(block.name, block.input)
                            tools_called.append({"tool": block.name, "result": tool_result})

            return {"success": False, "answer": None, "tools": tools_called, "error": "Max loops reached"}
        except Exception as e:
            logger.error(f"Error: {e}")
            return {"success": False, "answer": None, "tools": [], "error": str(e)}

    def _run_tool(self, name: str, args: Dict) -> Any:
        logger.info(f"Running {name}")
        try:
            if name == "read_file":
                return read_file(args.get("filepath", ""))
            elif name == "list_files":
                return list_files(args.get("directory", ""), args.get("extension"))
            elif name == "write_file":
                return write_file(args.get("filepath", ""), args.get("content", ""))
            elif name == "search_in_file":
                return search_in_file(args.get("filepath", ""), args.get("keyword", ""))
            return {"error": f"Unknown tool: {name}"}
        except Exception as e:
            return {"error": str(e)}

    def reset(self):
        self.messages = []

    def history(self):
        return self.messages

