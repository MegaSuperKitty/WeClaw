# -*- coding: utf-8 -*-
"""AskHuman tool: pause and wait for human input."""

from __future__ import annotations

from typing import Callable, Dict, Optional
import threading
import time

from integrations.mcp.openai_tool import Tool


class AskHumanTool(Tool):
    """Represent the AskHumanTool component.
    
    Attributes:
        _manager (AskHumanManager): Instance field for manager.
        _active_user_id (Optional[str]): Unique identifier used by the instance.
        _ask_handler (Optional[Callable[[str, str], None]]): Instance field for ask handler.
        _cancel_checker (Optional[Callable[[], bool]]): Instance field for cancel checker.
    """
    def __init__(self, manager: "AskHumanManager"):
        """Initialize ask human tool state and dependencies.
        
        Args:
            manager (AskHumanManager): Input value for manager.
        
        Returns:
            None: This method does not return a value.
        """
        self._manager = manager
        self._active_user_id: Optional[str] = None
        self._ask_handler: Optional[Callable[[str, str], None]] = None
        self._cancel_checker: Optional[Callable[[], bool]] = None
        self._non_blocking: bool = False
        super().__init__(
            name="ask_human",
            description=(
                "Ask the user a question and wait for the reply. "
                "Use when you must confirm or request missing info."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Question to ask the user."},
                },
                "required": ["question"],
            },
        )

    def set_context(
        self,
        user_id: str,
        on_ask: Optional[Callable[[str, str], None]] = None,
        cancel_checker: Optional[Callable[[], bool]] = None,
        non_blocking: bool = False,
    ):
        """Set context.
        
        Args:
            user_id (str): Identifier for the user.
            on_ask (Optional[Callable[[str, str], None]]): Input value for on ask.
            cancel_checker (Optional[Callable[[], bool]]): Callable that returns True when execution should stop.
        
        Returns:
            None: This method does not return a value.
        """
        self._active_user_id = user_id
        if on_ask is not None:
            self._ask_handler = on_ask
        if cancel_checker is not None:
            self._cancel_checker = cancel_checker
        self._non_blocking = bool(non_blocking)

    def _execute(self, **kwargs):
        """Internal helper to execute.
        
        Args:
            **kwargs (Any): Additional keyword arguments for extensibility.
        
        Returns:
            Any: Result produced by this function.
        
        Note:
            This is a private helper used internally by the module/class.
        """
        question = (kwargs.get("question") or "").strip()
        if not question:
            return "AskHuman error: question is required."
        if not self._active_user_id:
            return "AskHuman error: user context not bound."
        if self._non_blocking:
            if self._ask_handler:
                self._ask_handler(self._active_user_id, question)
            return ""
        return self._manager.ask(
            self._active_user_id,
            question,
            on_ask=self._ask_handler,
            cancel_checker=self._cancel_checker,
        )


class AskHumanManager:
    """Represent the AskHumanManager component.
    
    Attributes:
        _lock (Any): Instance field for lock.
        _pending (Dict[str, Dict[str, object]]): Instance field for pending.
    """
    def __init__(self):
        """Initialize ask human manager state and dependencies.
        
        Args:
            None.
        
        Returns:
            None: This method does not return a value.
        """
        self._lock = threading.Lock()
        self._pending: Dict[str, Dict[str, object]] = {}

    def has_pending(self, user_id: str) -> bool:
        """Has pending.
        
        Args:
            user_id (str): Identifier for the user.
        
        Returns:
            bool: True when the condition is satisfied; otherwise False.
        """
        with self._lock:
            return user_id in self._pending

    def ask(
        self,
        user_id: str,
        question: str,
        on_ask: Optional[Callable[[str, str], None]] = None,
        cancel_checker: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Ask.
        
        Args:
            user_id (str): Identifier for the user.
            question (str): Input value for question.
            on_ask (Optional[Callable[[str, str], None]]): Input value for on ask.
            cancel_checker (Optional[Callable[[], bool]]): Callable that returns True when execution should stop.
        
        Returns:
            str: Result produced by this function.
        """
        event = threading.Event()
        with self._lock:
            self._pending[user_id] = {
                "event": event,
                "response": None,
                "question": question,
            }
        if on_ask:
            on_ask(user_id, question)

        while True:
            if cancel_checker and cancel_checker():
                self.cancel(user_id)
                return ""
            if event.wait(timeout=0.2):
                break
        with self._lock:
            data = self._pending.pop(user_id, None)
        if not data:
            return ""
        response = data.get("response")
        return "" if response is None else str(response).strip()

    def provide(self, user_id: str, response: str) -> bool:
        """Provide.
        
        Args:
            user_id (str): Identifier for the user.
            response (str): Input value for response.
        
        Returns:
            bool: Result produced by this function.
        """
        with self._lock:
            data = self._pending.get(user_id)
            if not data:
                return False
            data["response"] = response
            event: threading.Event = data["event"]
            event.set()
        return True

    def cancel(self, user_id: str) -> None:
        """Cancel.
        
        Args:
            user_id (str): Identifier for the user.
        
        Returns:
            None: This method does not return a value.
        """
        with self._lock:
            data = self._pending.get(user_id)
            if not data:
                return
            data["response"] = ""
            event: threading.Event = data["event"]
            event.set()
