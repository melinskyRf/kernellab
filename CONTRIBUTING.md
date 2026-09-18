# Contributing to Kernel Lab

Thank you for your interest in contributing to Kernel Lab!

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/your-username/kernellab.git
   cd kernel-lab
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests to verify setup:
   ```bash
   make test
   ```

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make your changes

3. Run linting and type checking:
   ```bash
   make lint
   make typecheck
   ```

4. Run the full test suite:
   ```bash
   make test
   ```

5. Commit with a clear message

6. Push and create a Pull Request

## Code Guidelines

- Use type hints everywhere
- Follow existing code patterns
- Keep functions small and focused
- Write tests for new functionality
- Update documentation as needed

## Architecture

See [docs/architecture.md](docs/architecture.md) for the project architecture.

Key principles:
- Domain layer is independent
- Application services orchestrate domain and infrastructure
- Providers are pluggable
- CLI and API share the same application layer
- No business logic in API routes or CLI commands

## Testing

- Unit tests go in `tests/unit/`
- Integration tests go in `tests/integration/`
- CLI tests go in `tests/cli/`
- Use temporary directories for test isolation
- Never depend on the real filesystem

## Pull Requests

- Keep PRs focused on a single change
- Include tests for new functionality
- Update documentation if needed
- Ensure all CI checks pass
