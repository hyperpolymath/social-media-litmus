# Contributing to NUJ Social Media Ethics Monitor

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

This project serves the journalism community and union movement. Please be respectful and professional in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork
3. Set up development environment: `./tools/scripts/setup-dev.sh`
4. Create a feature branch: `git checkout -b feature/your-feature-name`

## Development Workflow

### Before Making Changes

1. Check existing issues and pull requests
2. Discuss major changes in an issue first
3. Ensure you have the latest changes: `git pull origin main`

### Making Changes

1. Write clear, commented code
2. Follow the project's code style
3. Add tests for new features
4. Update documentation as needed

### Code Style

#### Rust (Collector)
```bash
cargo fmt
cargo clippy
cargo test
```

#### Python (Analyzer)
```bash
black .
isort .
mypy app/
pytest
```

#### Node.js (Publisher)
```bash
npm run lint
npm run format
npm test
```

#### Elixir (Dashboard)
```bash
mix format
mix test
```

### Running Tests

```bash
# All services
./tools/scripts/test-all.sh

# Individual service
cd services/<service-name>
# Run service-specific tests
```

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add support for Mastodon platform
fix: correct checksum calculation in collector
docs: update API documentation
test: add tests for guidance generation
refactor: simplify database query logic
```

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update documentation in relevant service directories
3. Ensure all tests pass: `./tools/scripts/test-all.sh`
4. Update CLAUDE.md if project context changes
5. Request review from maintainers

### PR Title Format

```
[Service] Brief description

Example:
[Collector] Add Mastodon platform support
[Analyzer] Improve NLP confidence scoring
[Publisher] Fix grace period calculation
[Dashboard] Add real-time change notifications
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- List of specific changes
- Another change

## Testing
How have you tested this?

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Closes #123
```

## Development Guidelines

### Security

- Never commit API keys or credentials
- Use environment variables for secrets
- Follow OWASP guidelines for web security
- Report security vulnerabilities privately

### Performance

- Profile code for bottlenecks
- Use appropriate data structures
- Minimize database queries
- Cache when appropriate

### Documentation

- Comment complex logic
- Update README files
- Keep API documentation current
- Add examples for new features

## Project Structure

```
social-media-dipstick/
├── services/          # Microservices
│   ├── collector/    # Rust
│   ├── analyzer/     # Python
│   ├── dashboard/    # Elixir
│   └── publisher/    # Node.js
├── infrastructure/   # Database, monitoring
├── tools/           # CLI tools, scripts
├── shared/          # Shared schemas, types
└── docs/            # Documentation
```

## Service-Specific Guidelines

### Collector (Rust)
- Use Result<T, E> for error handling
- Implement proper retry logic
- Respect platform rate limits
- Cache API responses when appropriate

### Analyzer (Python)
- Use type hints
- Handle NLP errors gracefully
- Validate AI outputs
- Monitor API costs

### Publisher (Node.js)
- Implement all 19 safety guardrails
- Test rollback functionality
- Track email delivery metrics
- Ensure GDPR compliance

### Dashboard (Elixir/Phoenix)
- Use LiveView for real-time updates
- Optimize database queries
- Implement proper authentication
- Cache expensive computations

## Testing Requirements

### Unit Tests
- Test individual functions/methods
- Mock external dependencies
- Achieve >80% code coverage

### Integration Tests
- Test service interactions
- Use test database
- Clean up after tests

### E2E Tests
- Test complete workflows
- Use realistic data
- Test error scenarios

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create GitHub release
6. Deploy to staging
7. Smoke test staging
8. Deploy to production

## Getting Help

- Check documentation in `/docs`
- Review existing issues
- Ask in discussions
- Email: [Contact TBD]

## Recognition

Contributors will be acknowledged in:
- CONTRIBUTORS.md file
- Release notes
- Annual reports

Thank you for contributing to the NUJ Social Media Ethics Monitor!
