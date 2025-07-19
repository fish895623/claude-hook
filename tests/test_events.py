"""Tests for core event data classes."""

import json

import pytest

from claude_hooks.core.events import (
    HookDecision,
    HookEvent,
    HookEventType,
    HookResponse,
    NotificationEvent,
    PostToolUseEvent,
    PreCompactEvent,
    PreToolUseEvent,
    StopEvent,
    SubagentStopEvent,
    UserPromptSubmitEvent,
)


class TestHookEventType:
    """Test HookEventType enum."""

    def test_event_type_values(self):
        """Test that event types match Claude Code specification."""
        assert HookEventType.PRE_TOOL_USE == "PreToolUse"
        assert HookEventType.POST_TOOL_USE == "PostToolUse"
        assert HookEventType.NOTIFICATION == "Notification"
        assert HookEventType.USER_PROMPT_SUBMIT == "UserPromptSubmit"
        assert HookEventType.STOP == "Stop"
        assert HookEventType.SUBAGENT_STOP == "SubagentStop"
        assert HookEventType.PRE_COMPACT == "PreCompact"


class TestHookDecision:
    """Test HookDecision enum."""

    def test_decision_values(self):
        """Test decision values match specification."""
        assert HookDecision.APPROVE == "approve"
        assert HookDecision.BLOCK == "block"
        assert HookDecision.UNDEFINED == "undefined"


class TestHookEvent:
    """Test HookEvent base class."""

    def test_hook_event_creation(self):
        """Test basic HookEvent creation."""
        event = HookEvent(
            session_id="test-session",
            transcript_path="/path/to/transcript.md",
            cwd="/home/user/project",
            hook_event_name=HookEventType.PRE_TOOL_USE,
        )
        assert event.session_id == "test-session"
        assert event.transcript_path == "/path/to/transcript.md"
        assert event.cwd == "/home/user/project"
        assert event.hook_event_name == HookEventType.PRE_TOOL_USE

    def test_hook_event_with_tool_input(self):
        """Test HookEvent with tool_input."""
        tool_input = {"command": "ls -la", "description": "List files"}
        event = HookEvent(
            session_id="test-session",
            transcript_path="/path/to/transcript.md",
            cwd="/home/user/project",
            hook_event_name=HookEventType.PRE_TOOL_USE,
            tool_input=tool_input,
        )
        assert event.tool_input == tool_input

    def test_hook_event_json_serialization(self):
        """Test HookEvent JSON serialization."""
        event = HookEvent(
            session_id="test-session",
            transcript_path="/path/to/transcript.md",
            cwd="/home/user/project",
            hook_event_name=HookEventType.POST_TOOL_USE,
        )
        json_str = event.to_json()

        # Verify it's valid JSON
        data = json.loads(json_str)
        assert data["session_id"] == "test-session"
        assert data["hook_event_name"] == "PostToolUse"

    def test_hook_event_json_deserialization(self):
        """Test HookEvent JSON deserialization."""
        event = HookEvent(
            session_id="test-session",
            transcript_path="/path/to/transcript.md",
            cwd="/home/user/project",
            hook_event_name=HookEventType.NOTIFICATION,
        )
        json_str = event.to_json()

        # Deserialize and verify
        deserialized = HookEvent.from_json(json_str)
        assert deserialized.session_id == event.session_id
        assert deserialized.hook_event_name == event.hook_event_name


class TestPreToolUseEvent:
    """Test PreToolUseEvent data class."""

    def test_pre_tool_use_event_creation(self):
        """Test PreToolUseEvent creation."""
        event = PreToolUseEvent(
            session_id="test-session",
            transcript_path="/path/to/transcript.md",
            cwd="/home/user/project",
            hook_event_name=HookEventType.PRE_TOOL_USE,
            tool_name="Bash",
            tool_input={"command": "ls", "description": "List files"},
        )

        assert event.hook_event_name == HookEventType.PRE_TOOL_USE
        assert event.tool_name == "Bash"
        assert event.tool_input["command"] == "ls"

    def test_pre_tool_use_event_validation(self):
        """Test PreToolUseEvent validates event type."""
        with pytest.raises(ValueError, match="Event type must be PreToolUse"):
            PreToolUseEvent(
                session_id="test-session",
                transcript_path="/path/to/transcript.md",
                cwd="/home/user/project",
                hook_event_name=HookEventType.POST_TOOL_USE,  # Wrong type
                tool_name="Edit",
            )


class TestPostToolUseEvent:
    """Test PostToolUseEvent data class."""

    def test_post_tool_use_event_creation(self):
        """Test PostToolUseEvent creation."""
        event = PostToolUseEvent(
            session_id="test-session",
            transcript_path="/path/to/transcript.md",
            cwd="/home/user/project",
            hook_event_name=HookEventType.POST_TOOL_USE,
            tool_name="Write",
            tool_output="File written successfully",
            success=True,
        )

        assert event.hook_event_name == HookEventType.POST_TOOL_USE
        assert event.tool_name == "Write"
        assert event.tool_output == "File written successfully"
        assert event.success is True


class TestNotificationEvent:
    """Test NotificationEvent data class."""

    def test_notification_event_creation(self):
        """Test NotificationEvent creation."""
        event = NotificationEvent(
            session_id="test-session",
            transcript_path="/path/to/transcript.md",
            cwd="/home/user/project",
            hook_event_name=HookEventType.NOTIFICATION,
            notification_type="user_input_required",
            message="Waiting for user input",
        )

        assert event.hook_event_name == HookEventType.NOTIFICATION
        assert event.notification_type == "user_input_required"
        assert event.message == "Waiting for user input"


class TestUserPromptSubmitEvent:
    """Test UserPromptSubmitEvent data class."""

    def test_user_prompt_submit_event_creation(self):
        """Test UserPromptSubmitEvent creation."""
        event = UserPromptSubmitEvent(
            session_id="test-session",
            transcript_path="/path/to/transcript.md",
            cwd="/home/user/project",
            hook_event_name=HookEventType.USER_PROMPT_SUBMIT,
            prompt="Create a new Python script",
        )

        assert event.hook_event_name == HookEventType.USER_PROMPT_SUBMIT
        assert event.prompt == "Create a new Python script"


class TestStopEvent:
    """Test StopEvent data class."""

    def test_stop_event_creation(self):
        """Test StopEvent creation."""
        event = StopEvent(
            session_id="test-session",
            transcript_path="/path/to/transcript.md",
            cwd="/home/user/project",
            hook_event_name=HookEventType.STOP,
            response_complete=True,
        )

        assert event.hook_event_name == HookEventType.STOP
        assert event.response_complete is True


class TestSubagentStopEvent:
    """Test SubagentStopEvent data class."""

    def test_subagent_stop_event_creation(self):
        """Test SubagentStopEvent creation."""
        task_result = {"status": "completed", "output": "Task finished"}
        event = SubagentStopEvent(
            session_id="test-session",
            transcript_path="/path/to/transcript.md",
            cwd="/home/user/project",
            hook_event_name=HookEventType.SUBAGENT_STOP,
            subagent_id="subagent-123",
            task_result=task_result,
        )

        assert event.hook_event_name == HookEventType.SUBAGENT_STOP
        assert event.subagent_id == "subagent-123"
        assert event.task_result == task_result


class TestPreCompactEvent:
    """Test PreCompactEvent data class."""

    def test_pre_compact_event_creation(self):
        """Test PreCompactEvent creation."""
        event = PreCompactEvent(
            session_id="test-session",
            transcript_path="/path/to/transcript.md",
            cwd="/home/user/project",
            hook_event_name=HookEventType.PRE_COMPACT,
            compact_reason="Token limit reached",
        )

        assert event.hook_event_name == HookEventType.PRE_COMPACT
        assert event.compact_reason == "Token limit reached"


class TestHookResponse:
    """Test HookResponse data class."""

    def test_continue_response(self):
        """Test continue response creation."""
        response = HookResponse.continue_response("Everything looks good")
        assert response.continue_ is True
        assert response.decision == HookDecision.APPROVE
        assert response.reason == "Everything looks good"

    def test_block_response(self):
        """Test block response creation."""
        response = HookResponse.block_response("Access denied", "Unauthorized file")
        assert response.continue_ is False
        assert response.decision == HookDecision.BLOCK
        assert response.reason == "Access denied"
        assert response.stop_reason == "Unauthorized file"

    def test_feedback_response(self):
        """Test feedback response creation."""
        response = HookResponse.feedback_response("Consider using better names", suppress_output=True)
        assert response.continue_ is True
        assert response.decision == HookDecision.UNDEFINED
        assert response.reason == "Consider using better names"
        assert response.suppress_output is True

    def test_response_json_serialization(self):
        """Test HookResponse JSON serialization with correct field names."""
        response = HookResponse.continue_response("Test reason")
        json_str = response.to_json()

        data = json.loads(json_str)
        assert data["continue"] is True  # Uses alias
        assert data["decision"] == "approve"
        assert data["reason"] == "Test reason"
        assert "suppressOutput" in data  # Uses alias

    def test_response_json_roundtrip(self):
        """Test HookResponse JSON serialization roundtrip."""
        original = HookResponse.block_response("Test block", "Test stop")
        json_str = original.to_json()
        deserialized = HookResponse.from_json(json_str)

        assert deserialized.continue_ == original.continue_
        assert deserialized.decision == original.decision
        assert deserialized.reason == original.reason
        assert deserialized.stop_reason == original.stop_reason
