"""JSON event parser and validator for Claude Hook system using Pydantic."""

from __future__ import annotations

import json
from typing import Any, ClassVar

from pydantic import ValidationError as PydanticValidationError

from .events import (
    AnyHookEvent,
    HookEvent,
    HookEventType,
    NotificationEvent,
    PostToolUseEvent,
    PreCompactEvent,
    PreToolUseEvent,
    StopEvent,
    SubagentStopEvent,
    UserPromptSubmitEvent,
)


class EventParseError(Exception):
    """Base exception for event parsing errors."""

    def __init__(self, message: str, original_data: str | None = None) -> None:
        super().__init__(message)
        self.original_data = original_data


class JSONParseError(EventParseError):
    """Exception for JSON parsing failures."""


class ValidationError(EventParseError):
    """Exception for event validation failures."""

    def __init__(
        self,
        message: str,
        validation_errors: list[str] | None = None,
        original_data: str | None = None,
    ) -> None:
        super().__init__(message, original_data)
        self.validation_errors = validation_errors or []


class UnknownEventTypeError(EventParseError):
    """Exception for unknown or unsupported event types."""

    def __init__(self, event_type: str, original_data: str | None = None) -> None:
        message = f"Unknown event type: {event_type}"
        super().__init__(message, original_data)
        self.event_type = event_type


class EventParser:
    """Factory class for parsing and validating Claude Code hook events."""

    # Registry mapping hook event names to their corresponding Pydantic models
    EVENT_TYPE_REGISTRY: ClassVar[dict[HookEventType, type[HookEvent]]] = {
        HookEventType.PRE_TOOL_USE: PreToolUseEvent,
        HookEventType.POST_TOOL_USE: PostToolUseEvent,
        HookEventType.NOTIFICATION: NotificationEvent,
        HookEventType.USER_PROMPT_SUBMIT: UserPromptSubmitEvent,
        HookEventType.STOP: StopEvent,
        HookEventType.SUBAGENT_STOP: SubagentStopEvent,
        HookEventType.PRE_COMPACT: PreCompactEvent,
    }

    @classmethod
    def parse(cls, json_input: str) -> AnyHookEvent:
        """
        Parse and validate a JSON string into the appropriate hook event object.

        Args:
            json_input: Raw JSON string from Claude Code

        Returns:
            Validated event object of the appropriate type

        Raises:
            JSONParseError: If the JSON is malformed
            ValidationError: If the event data fails validation
            UnknownEventTypeError: If the event type is not supported
        """
        # Parse JSON string to dict
        try:
            data = json.loads(json_input)
        except json.JSONDecodeError as e:
            msg = f"Failed to parse JSON: {e}"
            raise JSONParseError(msg, original_data=json_input) from e

        # Delegate to dict parsing method
        return cls.parse_dict(data, original_json=json_input)

    @classmethod
    def parse_dict(
        cls, data: dict[str, Any], original_json: str | None = None
    ) -> AnyHookEvent:
        """
        Parse and validate a dictionary into the appropriate hook event object.

        Args:
            data: Dictionary containing event data
            original_json: Original JSON string for error context

        Returns:
            Validated event object of the appropriate type

        Raises:
            ValidationError: If the event data fails validation
            UnknownEventTypeError: If the event type is not supported
        """
        if not isinstance(data, dict):
            msg = f"Expected dictionary, got {type(data).__name__}"
            raise ValidationError(msg, original_data=original_json)

        # Extract and validate hook_event_name
        hook_event_name = data.get("hook_event_name")
        if not hook_event_name:
            msg = "Missing required field: hook_event_name"
            raise ValidationError(msg, original_data=original_json)

        # Convert string to enum if needed
        try:
            if isinstance(hook_event_name, str):
                event_type = HookEventType(hook_event_name)
            else:
                event_type = hook_event_name
        except ValueError:
            raise UnknownEventTypeError(
                str(hook_event_name), original_data=original_json
            ) from None

        # Get the appropriate event class from registry
        event_class = cls.EVENT_TYPE_REGISTRY.get(event_type)
        if not event_class:
            raise UnknownEventTypeError(
                str(event_type), original_data=original_json
            )

        # Use Pydantic validation to create the event object
        try:
            return event_class.model_validate(data)
        except PydanticValidationError as e:
            # Extract validation error details
            error_messages = []
            for error in e.errors():
                location = " -> ".join(str(loc) for loc in error["loc"])
                message = error["msg"]
                error_messages.append(f"{location}: {message}")

            msg = f"Validation failed for {event_type.value} event"
            raise ValidationError(
                msg,
                validation_errors=error_messages,
                original_data=original_json,
            ) from e

    @classmethod
    def get_supported_event_types(cls) -> list[HookEventType]:
        """Get list of all supported event types."""
        return list(cls.EVENT_TYPE_REGISTRY.keys())

    @classmethod
    def is_supported_event_type(cls, event_type: str | HookEventType) -> bool:
        """Check if an event type is supported."""
        try:
            if isinstance(event_type, str):
                event_type = HookEventType(event_type)
        except (ValueError, AttributeError):
            return False
        else:
            return event_type in cls.EVENT_TYPE_REGISTRY


# Convenience function for direct parsing
def parse_hook_event(json_input: str) -> AnyHookEvent:
    """
    Convenience function to parse a hook event from JSON.

    Args:
        json_input: Raw JSON string from Claude Code

    Returns:
        Validated event object of the appropriate type
    """
    return EventParser.parse(json_input)
