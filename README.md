# Claude Hook

Extensible hook system for Claude Code with auto-formatting, security controls, and workflow automation.

## Features

- **Auto-formatting**: Automatic code formatting with black, prettier, gofmt, rustfmt
- **Security Controls**: File protection and security validation
- **Notifications**: Desktop notifications for Claude Code events  
- **Git Integration**: Automated git workflows and commit validation
- **Testing**: Automated test execution after code changes
- **Extensible**: Plugin architecture for custom hook types

## Installation

```bash
uv add claude-hook
```

## Quick Start

```bash
# Initialize hook configuration
claude-hook init

# Configure hooks
claude-hook config

# Test hook system
claude-hook test
```

## Development

```bash
# Clone repository
git clone <repository-url>
cd claude-hook

# Install dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black src/ tests/
uv run ruff check src/ tests/
```

## License

MIT