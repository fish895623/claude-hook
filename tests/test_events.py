"""Tests for core event data classes and parser."""

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
from claude_hooks.core.parser import (
    EventParser,
    JSONParseError,
    UnknownEventTypeError,
    ValidationError,
    parse_hook_event,
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


class TestEventParser:
    """Test EventParser JSON parsing and validation."""

    def test_event_type_registry_completeness(self):
        """Test that all event types are in registry."""
        expected_types = {
            HookEventType.PRE_TOOL_USE,
            HookEventType.POST_TOOL_USE,
            HookEventType.NOTIFICATION,
            HookEventType.USER_PROMPT_SUBMIT,
            HookEventType.STOP,
            HookEventType.SUBAGENT_STOP,
            HookEventType.PRE_COMPACT,
        }
        registry_types = set(EventParser.EVENT_TYPE_REGISTRY.keys())
        assert registry_types == expected_types

    def test_get_supported_event_types(self):
        """Test getting list of supported event types."""
        expected_count = 7  # Number of supported event types
        supported = EventParser.get_supported_event_types()
        assert len(supported) == expected_count
        assert HookEventType.PRE_TOOL_USE in supported

    def test_is_supported_event_type(self):
        """Test checking if event type is supported."""
        assert EventParser.is_supported_event_type("PreToolUse")
        assert EventParser.is_supported_event_type(HookEventType.POST_TOOL_USE)
        assert not EventParser.is_supported_event_type("InvalidType")
        assert not EventParser.is_supported_event_type(None)

    def test_parse_pre_tool_use_event(self):
        """Test parsing valid PreToolUse event."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "ls", "description": "List files"},
        }
        json_str = json.dumps(json_data)

        event = EventParser.parse(json_str)
        assert isinstance(event, PreToolUseEvent)
        assert event.hook_event_name == HookEventType.PRE_TOOL_USE
        assert event.tool_name == "Bash"
        assert event.session_id == "test-session"

    def test_parse_post_tool_use_event(self):
        """Test parsing valid PostToolUse event."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "PostToolUse",
            "tool_name": "Write",
            "tool_output": "File created successfully",
            "success": True,
        }
        json_str = json.dumps(json_data)

        event = EventParser.parse(json_str)
        assert isinstance(event, PostToolUseEvent)
        assert event.hook_event_name == HookEventType.POST_TOOL_USE
        assert event.tool_name == "Write"
        assert event.success is True

    def test_parse_notification_event(self):
        """Test parsing valid Notification event."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "Notification",
            "notification_type": "info",
            "message": "Processing complete",
        }
        json_str = json.dumps(json_data)

        event = EventParser.parse(json_str)
        assert isinstance(event, NotificationEvent)
        assert event.notification_type == "info"
        assert event.message == "Processing complete"

    def test_parse_user_prompt_submit_event(self):
        """Test parsing valid UserPromptSubmit event."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Help me write a Python script",
        }
        json_str = json.dumps(json_data)

        event = EventParser.parse(json_str)
        assert isinstance(event, UserPromptSubmitEvent)
        assert event.prompt == "Help me write a Python script"

    def test_parse_stop_event(self):
        """Test parsing valid Stop event."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "Stop",
            "response_complete": True,
        }
        json_str = json.dumps(json_data)

        event = EventParser.parse(json_str)
        assert isinstance(event, StopEvent)
        assert event.response_complete is True

    def test_parse_subagent_stop_event(self):
        """Test parsing valid SubagentStop event."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "SubagentStop",
            "subagent_id": "subagent-123",
            "task_result": {"status": "completed"},
        }
        json_str = json.dumps(json_data)

        event = EventParser.parse(json_str)
        assert isinstance(event, SubagentStopEvent)
        assert event.subagent_id == "subagent-123"

    def test_parse_pre_compact_event(self):
        """Test parsing valid PreCompact event."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "PreCompact",
            "compact_reason": "Token limit reached",
        }
        json_str = json.dumps(json_data)

        event = EventParser.parse(json_str)
        assert isinstance(event, PreCompactEvent)
        assert event.compact_reason == "Token limit reached"

    def test_parse_dict_method(self):
        """Test parsing from dictionary."""
        data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "Stop",
            "response_complete": False,
        }

        event = EventParser.parse_dict(data)
        assert isinstance(event, StopEvent)
        assert event.response_complete is False

    def test_convenience_function(self):
        """Test parse_hook_event convenience function."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "Notification",
            "notification_type": "warning",
        }
        json_str = json.dumps(json_data)

        event = parse_hook_event(json_str)
        assert isinstance(event, NotificationEvent)
        assert event.notification_type == "warning"

    def test_parse_with_extra_fields(self):
        """Test parsing with extra fields (should be allowed)."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "Stop",
            "response_complete": True,
            "extra_field": "extra_value",  # Extra field
            "another_extra": 123,
        }
        json_str = json.dumps(json_data)

        event = EventParser.parse(json_str)
        assert isinstance(event, StopEvent)
        assert event.response_complete is True

    def test_json_parse_error_invalid_json(self):
        """Test JSONParseError for invalid JSON."""
        invalid_json = '{"incomplete": json'

        with pytest.raises(JSONParseError) as exc_info:
            EventParser.parse(invalid_json)

        assert "Failed to parse JSON" in str(exc_info.value)
        assert exc_info.value.original_data == invalid_json

    def test_json_parse_error_not_json_object(self):
        """Test ValidationError for non-object JSON."""
        json_str = '"not an object"'

        with pytest.raises(ValidationError) as exc_info:
            EventParser.parse(json_str)

        assert "Expected dictionary" in str(exc_info.value)

    def test_validation_error_missing_hook_event_name(self):
        """Test ValidationError for missing hook_event_name."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            # Missing hook_event_name
        }
        json_str = json.dumps(json_data)

        with pytest.raises(ValidationError) as exc_info:
            EventParser.parse(json_str)

        assert "Missing required field: hook_event_name" in str(exc_info.value)
        assert exc_info.value.original_data == json_str

    def test_unknown_event_type_error(self):
        """Test UnknownEventTypeError for unsupported event type."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "UnsupportedEventType",
        }
        json_str = json.dumps(json_data)

        with pytest.raises(UnknownEventTypeError) as exc_info:
            EventParser.parse(json_str)

        assert "Unknown event type: UnsupportedEventType" in str(exc_info.value)
        assert exc_info.value.event_type == "UnsupportedEventType"
        assert exc_info.value.original_data == json_str

    def test_validation_error_missing_required_field(self):
        """Test ValidationError for missing required field."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "PreToolUse",
            # Missing required tool_name field
        }
        json_str = json.dumps(json_data)

        with pytest.raises(ValidationError) as exc_info:
            EventParser.parse(json_str)

        assert "Validation failed for PreToolUse event" in str(exc_info.value)
        assert len(exc_info.value.validation_errors) > 0
        assert any("tool_name" in error for error in exc_info.value.validation_errors)

    def test_validation_error_wrong_field_type(self):
        """Test ValidationError for wrong field type."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "PostToolUse",
            "tool_name": "Write",
            "success": "not a boolean",  # Wrong type
        }
        json_str = json.dumps(json_data)

        with pytest.raises(ValidationError) as exc_info:
            EventParser.parse(json_str)

        assert "Validation failed for PostToolUse event" in str(exc_info.value)
        assert len(exc_info.value.validation_errors) > 0

    def test_parser_respects_event_type_in_data(self):
        """Test that parser creates correct event type based on hook_event_name."""
        json_data = {
            "session_id": "test-session",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "success": True,  # Add required field for PostToolUse
        }
        json_str = json.dumps(json_data)

        event = EventParser.parse(json_str)
        # Should parse as PostToolUse since that's what hook_event_name specifies
        assert isinstance(event, PostToolUseEvent)
        assert event.tool_name == "Bash"
        assert event.success is True

    def test_round_trip_parsing(self):
        """Test parsing an event that was serialized from a Pydantic model."""
        # Create an event
        original_event = PreToolUseEvent(
            session_id="round-trip-test",
            transcript_path="/path/to/transcript.md",
            cwd="/home/user/project",
            hook_event_name=HookEventType.PRE_TOOL_USE,
            tool_name="Edit",
            tool_input={"file_path": "/test.py", "content": "print('hello')"},
        )

        # Serialize to JSON
        json_str = original_event.to_json()

        # Parse back
        parsed_event = EventParser.parse(json_str)

        # Verify they're equivalent
        assert isinstance(parsed_event, PreToolUseEvent)
        assert parsed_event.session_id == original_event.session_id
        assert parsed_event.tool_name == original_event.tool_name
        assert parsed_event.tool_input == original_event.tool_input

    def test_unicode_handling(self):
        """Test parsing with Unicode characters."""
        json_data = {
            "session_id": "unicode-test",
            "transcript_path": "/path/to/transcript.md",
            "cwd": "/home/user/project",
            "hook_event_name": "Notification",
            "notification_type": "info",
            "message": "Processing complete ✅ 🎉 Unicode text: café naïve résumé",
        }
        json_str = json.dumps(json_data, ensure_ascii=False)

        event = EventParser.parse(json_str)
        assert isinstance(event, NotificationEvent)
        assert "café naïve résumé" in event.message
        assert "✅" in event.message
