"""Core event data classes and type definitions for Claude Hook system."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HookEventType(str, Enum):
    """Enumeration of all supported Claude Code hook event types."""

    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    NOTIFICATION = "Notification"
    USER_PROMPT_SUBMIT = "UserPromptSubmit"
    STOP = "Stop"
    SUBAGENT_STOP = "SubagentStop"
    PRE_COMPACT = "PreCompact"


class HookDecision(str, Enum):
    """Available decision values for hook responses."""

    APPROVE = "approve"
    BLOCK = "block"
    UNDEFINED = "undefined"


class ToolInfo(BaseModel):
    """Information about the tool being used."""

    name: str = Field(..., description="Name of the tool being used")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Tool parameters")

    model_config = ConfigDict(frozen=True)


class FileInfo(BaseModel):
    """Information about files involved in the event."""

    path: str = Field(..., description="File path")
    content: str | None = Field(None, description="File content if available")
    size: int | None = Field(None, description="File size in bytes")
    permissions: str | None = Field(None, description="File permissions")

    model_config = ConfigDict(frozen=True)


class HookEvent(BaseModel):
    """Base class for all Claude Code hook events following official specification."""

    session_id: str = Field(..., description="Claude Code session identifier")
    transcript_path: str = Field(..., description="Path to conversation transcript")
    cwd: str = Field(..., description="Current working directory")
    hook_event_name: HookEventType = Field(..., description="Type of hook event")

    # Additional fields that may be present in different event types
    tool_input: dict[str, Any] | None = Field(None, description="Tool input parameters")
    metadata: dict[str, Any] | None = Field(None, description="Additional event metadata")

    model_config = ConfigDict(frozen=True, extra="allow")

    def to_json(self) -> str:
        """Serialize event to JSON string."""
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> HookEvent:
        """Deserialize event from JSON string."""
        return cls.model_validate_json(json_str)


class PreToolUseEvent(HookEvent):
    """Event for PreToolUse hook - runs before tool execution."""

    tool_name: str = Field(..., description="Name of the tool being used")

    model_config = ConfigDict(frozen=True)

    @field_validator('hook_event_name')
    @classmethod
    def validate_event_type(cls, v):
        if v != HookEventType.PRE_TOOL_USE:
            msg = "Event type must be PreToolUse"
            raise ValueError(msg)
        return v


class PostToolUseEvent(HookEvent):
    """Event for PostToolUse hook - runs after tool execution."""

    tool_name: str = Field(..., description="Name of the tool that was used")
    tool_output: str | None = Field(None, description="Output from tool execution")
    success: bool = Field(..., description="Whether tool execution was successful")

    model_config = ConfigDict(frozen=True)

    @field_validator('hook_event_name')
    @classmethod
    def validate_event_type(cls, v):
        if v != HookEventType.POST_TOOL_USE:
            msg = "Event type must be PostToolUse"
            raise ValueError(msg)
        return v


class NotificationEvent(HookEvent):
    """Event for Notification hook - runs when Claude sends notifications."""

    notification_type: str = Field(..., description="Type of notification")
    message: str | None = Field(None, description="Notification message")

    model_config = ConfigDict(frozen=True)

    @field_validator('hook_event_name')
    @classmethod
    def validate_event_type(cls, v):
        if v != HookEventType.NOTIFICATION:
            msg = "Event type must be Notification"
            raise ValueError(msg)
        return v


class UserPromptSubmitEvent(HookEvent):
    """Event for UserPromptSubmit hook - runs when user submits a prompt."""

    prompt: str = Field(..., description="User's submitted prompt")

    model_config = ConfigDict(frozen=True)

    @field_validator('hook_event_name')
    @classmethod
    def validate_event_type(cls, v):
        if v != HookEventType.USER_PROMPT_SUBMIT:
            msg = "Event type must be UserPromptSubmit"
            raise ValueError(msg)
        return v


class StopEvent(HookEvent):
    """Event for Stop hook - runs when Claude finishes responding."""

    response_complete: bool = Field(..., description="Whether response was completed")

    model_config = ConfigDict(frozen=True)

    @field_validator('hook_event_name')
    @classmethod
    def validate_event_type(cls, v):
        if v != HookEventType.STOP:
            msg = "Event type must be Stop"
            raise ValueError(msg)
        return v


class SubagentStopEvent(HookEvent):
    """Event for SubagentStop hook - runs when subagent tasks complete."""

    subagent_id: str = Field(..., description="Identifier of the subagent")
    task_result: dict[str, Any] | None = Field(None, description="Result of subagent task")

    model_config = ConfigDict(frozen=True)

    @field_validator('hook_event_name')
    @classmethod
    def validate_event_type(cls, v):
        if v != HookEventType.SUBAGENT_STOP:
            msg = "Event type must be SubagentStop"
            raise ValueError(msg)
        return v


class PreCompactEvent(HookEvent):
    """Event for PreCompact hook - runs before conversation compaction."""

    compact_reason: str = Field(..., description="Reason for compaction")

    model_config = ConfigDict(frozen=True)

    @field_validator('hook_event_name')
    @classmethod
    def validate_event_type(cls, v):
        if v != HookEventType.PRE_COMPACT:
            msg = "Event type must be PreCompact"
            raise ValueError(msg)
        return v


class HookResponse(BaseModel):
    """Response to a Claude Code hook event following official specification."""

    continue_: bool = Field(..., alias="continue", description="Whether to continue execution")
    stop_reason: str | None = Field(None, alias="stopReason", description="Reason for stopping")
    suppress_output: bool = Field(False, alias="suppressOutput", description="Whether to suppress output")
    decision: HookDecision = Field(HookDecision.UNDEFINED, description="Hook decision")
    reason: str | None = Field(None, description="Explanation for the decision")

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    def to_json(self) -> str:
        """Serialize response to JSON string."""
        return self.model_dump_json(by_alias=True)

    @classmethod
    def from_json(cls, json_str: str) -> HookResponse:
        """Deserialize response from JSON string."""
        return cls.model_validate_json(json_str)

    @classmethod
    def continue_response(cls, reason: str | None = None) -> HookResponse:
        """Create a continue response."""
        return cls(
            continue_=True,
            decision=HookDecision.APPROVE,
            reason=reason
        )

    @classmethod
    def block_response(cls, reason: str, stop_reason: str | None = None) -> HookResponse:
        """Create a block response."""
        return cls(
            continue_=False,
            decision=HookDecision.BLOCK,
            reason=reason,
            stop_reason=stop_reason
        )

    @classmethod
    def feedback_response(cls, reason: str, suppress_output: bool = False) -> HookResponse:
        """Create a feedback response."""
        return cls(
            continue_=True,
            decision=HookDecision.UNDEFINED,
            reason=reason,
            suppress_output=suppress_output
        )


# Type alias for all specific event types
AnyHookEvent = (
    PreToolUseEvent
    | PostToolUseEvent
    | NotificationEvent
    | UserPromptSubmitEvent
    | StopEvent
    | SubagentStopEvent
    | PreCompactEvent
)
