class ChatServiceError(Exception):
    """Base exception for chat service."""


class MaxToolRoundsExceededError(ChatServiceError):
    """Raised when the model exceeds the allowed tool rounds."""