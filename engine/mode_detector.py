class ModeDetector:
    """
    Determines whether input should trigger:
    - Tool execution mode
    - Conversation mode

    Phase 1: Deterministic keyword-based detection.
    Designed to be extendable.
    """

    def __init__(self):
        # Keywords that strongly indicate system-level action
        self.tool_keywords = [
            "open",
            "delete",
            "remove",
            "create",
            "make",
            "launch",
            "run",
            "execute",
            "shutdown",
            "restart",
            "list files",
            "show files",
            "create folder",
            "delete folder",
            "make directory",
            "clear terminal",

            # timer
            "timer",
            "set timer",
            "start timer",
            "countdown"
        ]

        # Phrases that usually indicate conversation even if they contain keywords
        self.conversation_overrides = [
            "should i open",
            "why did it open",
            "how do i delete",
            "what does delete mean"
        ]

    def detect(self, user_input: str) -> str:
        """
        Returns:
            "tool" or "conversation"
        """

        text = user_input.lower().strip()

        # First check conversation overrides
        for phrase in self.conversation_overrides:
            if phrase in text:
                return "conversation"

        # Then check for tool keywords
        for keyword in self.tool_keywords:
            if keyword in text:
                return "tool"

        return "conversation"