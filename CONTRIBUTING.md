# Contributing to DocChat MCP Server

Thank you for your interest in contributing to DocChat MCP Server! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Use the issue template** if available
3. **Provide detailed information** including:
   - Operating system and version
   - Python version
   - Claude Desktop version
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Error messages and logs

### Suggesting Features

When suggesting new features:

1. **Check if the feature already exists** or is planned
2. **Explain the use case** and why it would be valuable
3. **Provide implementation ideas** if you have them
4. **Consider the scope** - prefer focused, well-defined features

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/Enkidu-png/docchat-mcp-server.git
   cd docchat-mcp-server
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

4. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pre-commit install
   ```

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run tests
   pytest

   # Run linting
   flake8 src/
   black --check src/
   isort --check-only src/

   # Type checking
   mypy src/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Coding Standards

### Python Style

- **PEP 8 compliance**: Use `black` for formatting
- **Import sorting**: Use `isort` for import organization
- **Type hints**: Add type hints for all public functions
- **Docstrings**: Use Google-style docstrings

### Code Organization

- **Modularity**: Keep functions and classes focused and small
- **Error handling**: Use proper exception handling with informative messages
- **Logging**: Use the project's logging configuration
- **Constants**: Define constants in appropriate config files

### Documentation

- **Function docstrings**: Describe parameters, return values, and exceptions
- **Class docstrings**: Explain the purpose and usage
- **README updates**: Update README.md for significant changes
- **Code comments**: Explain complex logic and business rules

### Testing

- **Unit tests**: Write tests for all new functionality
- **Integration tests**: Test MCP tool interactions
- **Test coverage**: Maintain good test coverage
- **Test naming**: Use descriptive test names that explain what is being tested

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_embedding_service.py

# Run with verbose output
pytest -v
```

### Writing Tests

```python
import pytest
from src.services.embedding_service import EmbeddingService

class TestEmbeddingService:
    @pytest.mark.asyncio
    async def test_generate_embedding(self):
        """Test that embedding generation works correctly."""
        service = EmbeddingService()
        text = "Test document content"

        embedding = await service.generate_embedding(text)

        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)
```

## 🚀 Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(search): add semantic similarity threshold configuration
fix(indexing): handle PDF parsing errors gracefully
docs: update installation instructions for Windows
```

## 🔍 Code Review Process

1. **Automated checks**: All PRs must pass CI/CD checks
2. **Code review**: At least one maintainer must review and approve
3. **Testing**: Ensure all tests pass and coverage is maintained
4. **Documentation**: Update documentation for user-facing changes

### Review Checklist

- [ ] Code follows project style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Security considerations addressed
- [ ] Performance impact considered

## 🛡️ Security

### Reporting Security Issues

**Do not create public issues for security vulnerabilities.**

Instead, email security concerns to: [security@yourproject.com]

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes

### Security Best Practices

- **Input validation**: Validate all user inputs
- **File access**: Implement proper file access controls
- **Dependencies**: Keep dependencies updated
- **Secrets**: Never commit secrets or API keys

## 📖 Documentation

### Documentation Types

- **API Documentation**: Auto-generated from docstrings
- **User Guide**: Step-by-step usage instructions
- **Developer Guide**: Technical implementation details
- **Examples**: Working code examples

### Building Documentation

```bash
cd docs/
make html  # Generate HTML documentation
make clean # Clean generated files
```

## 🎯 Project Goals

When contributing, keep these project goals in mind:

1. **Simplicity**: Keep the API simple and intuitive
2. **Performance**: Maintain fast query response times
3. **Privacy**: Ensure user data stays local
4. **Reliability**: Build robust error handling
5. **Compatibility**: Maintain MCP compliance
6. **Extensibility**: Design for future enhancements

## 📞 Getting Help

- **Discord/Slack**: Join our community chat (if available)
- **GitHub Discussions**: Ask questions and share ideas
- **Issues**: For bug reports and feature requests
- **Email**: For sensitive matters

## 🏆 Recognition

Contributors will be recognized in:

- **CONTRIBUTORS.md**: List of all contributors
- **Release notes**: Notable contributions highlighted
- **README**: Major contributors acknowledged

---

Thank you for contributing to DocChat MCP Server! Your help makes this project better for everyone. 🚀