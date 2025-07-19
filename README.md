# Claude Hook System

An extensible hook system for Claude Code with auto-formatting, security controls, and workflow automation.

## Overview

This project provides a robust, production-ready hook system that integrates with Claude Code to enable custom workflows, security controls, and automated responses to various events during AI-assisted development sessions.

## Features

- **Event-Driven Architecture**: Handles all 7 Claude Code hook event types
- **Pydantic Validation**: Type-safe JSON parsing with comprehensive error handling
- **Extensible Design**: Plugin-based architecture for custom hook processors
- **Security Controls**: Built-in validation and security filtering capabilities
- **Workflow Automation**: Automated responses and notifications
- **Comprehensive Testing**: 97% test coverage with edge case handling

## Supported Hook Events

The system supports all official Claude Code hook events:

- **PreToolUse**: Runs before tool execution
- **PostToolUse**: Runs after tool execution  
- **Notification**: Handles Claude notifications
- **UserPromptSubmit**: Processes user prompt submissions
- **Stop**: Handles conversation completion
- **SubagentStop**: Manages subagent task completion
- **PreCompact**: Handles conversation compaction events

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/fish895623/claude-hook.git
cd claude-hook

# Install dependencies using uv
uv sync

# Install development dependencies
uv sync --group dev
```

### Basic Usage

```python
from claude_hooks.core.parser import EventParser, parse_hook_event
from claude_hooks.core.events import HookResponse

# Parse a Claude Code hook event
json_event = '{"session_id": "test", "hook_event_name": "PreToolUse", ...}'
event = parse_hook_event(json_event)

# Create responses
response = HookResponse.continue_response("Approved")
response = HookResponse.block_response("Security violation detected")
response = HookResponse.feedback_response("Consider using safer alternatives")
```

### Event Processing

```python
from claude_hooks.core.parser import EventParser
from claude_hooks.core.events import PreToolUseEvent

# Type-safe event parsing
event = EventParser.parse(claude_json_input)

if isinstance(event, PreToolUseEvent):
    print(f"Tool {event.tool_name} is about to run")
    # Apply custom logic, security checks, etc.
```

## Architecture

### Core Components

- **`events.py`**: Pydantic models for all hook event types and responses
- **`parser.py`**: JSON parsing and validation with comprehensive error handling
- **`dispatcher.py`**: Event routing and processor management *(coming soon)*
- **`processors/`**: Custom hook processors for different event types *(coming soon)*

### Event Flow

```
Claude Code → JSON Event → Parser → Dispatcher → Processors → Response
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/claude_hooks

# Run specific test file
uv run pytest tests/test_events.py -v
```

### Code Quality

```bash
# Linting
uv run ruff check .

# Type checking
uv run mypy src/

# Formatting
uv run black src/ tests/
```

## Documentation

### Official Claude Code Hooks Documentation

- **[Hooks Guide](https://docs.anthropic.com/en/docs/claude-code/hooks-guide)**: Comprehensive guide to setting up and using hooks
- **[Hooks Reference](https://docs.anthropic.com/en/docs/claude-code/hooks)**: Complete API reference and event specifications

### Key Documentation Sections

- **Event Types**: Complete specification of all 7 hook event types
- **Response Format**: How to structure responses to control Claude Code behavior
- **Configuration**: Setting up hooks in your Claude Code environment
- **Security**: Best practices for secure hook implementations
- **Examples**: Real-world hook implementation examples

## Configuration

Configure hooks in your Claude Code environment by creating hook scripts that use this library:

```bash
# Example hook script
#!/usr/bin/env python3
import sys
from claude_hooks.core.parser import parse_hook_event
from claude_hooks.core.events import HookResponse

# Parse the event from Claude Code
event_json = sys.stdin.read()
event = parse_hook_event(event_json)

# Process the event and create response
response = HookResponse.continue_response("Processing approved")

# Return response to Claude Code
print(response.to_json())
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Run the test suite: `uv run pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Status

- ✅ **Event Data Models**: Complete Pydantic models for all hook types
- ✅ **JSON Parser**: Robust parsing with validation and error handling  
- ✅ **Test Suite**: Comprehensive testing with 97% coverage
- 🔄 **Event Dispatcher**: In development (Task 2.3)
- 📋 **Hook Processors**: Planned
- 📋 **Security Controls**: Planned
- 📋 **Notification System**: Planned

## Links

- **Repository**: https://github.com/fish895623/claude-hook
- **Claude Code Hooks Guide**: https://docs.anthropic.com/en/docs/claude-code/hooks-guide
- **Claude Code Hooks Reference**: https://docs.anthropic.com/en/docs/claude-code/hooks
- **Issues**: https://github.com/fish895623/claude-hook/issues

---

Built with ❤️ for the Claude Code community