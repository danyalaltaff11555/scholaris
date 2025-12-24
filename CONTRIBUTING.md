# Contributing to Scholaris

Thank you for your interest in contributing to Scholaris. This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Making Changes](#making-changes)
6. [Testing](#testing)
7. [Submitting Changes](#submitting-changes)
8. [Review Process](#review-process)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Prioritize the project's goals over personal preferences

### Unacceptable Behavior

- Harassment or discrimination of any kind
- Trolling or inflammatory comments
- Publishing private information without permission
- Other conduct inappropriate in a professional setting

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Neo4j and Redis (for testing)
- Familiarity with the codebase architecture

### Finding Issues to Work On

1. Check the [Issues](https://github.com/danyalaltaff11555/scholaris/issues) page
2. Look for issues labeled `good first issue` or `help wanted`
3. Comment on the issue to express interest
4. Wait for maintainer assignment before starting work

### Asking Questions

- Use GitHub Discussions for general questions
- Use Issues for bug reports and feature requests
- Join our community chat for real-time discussion

## Development Setup

### Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/danyalaltaff11555/scholaris.git

# Add upstream remote
git remote add upstream https://github.com/danyalaltaff11555/scholaris.git
```

### Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Database Setup

```bash
# Start databases with Docker
docker-compose up -d

# Initialize schema
python scripts/setup_databases.py
```

### Verify Setup

```bash
# Run tests
pytest

# Check code formatting
black --check src/

# Run type checker
mypy src/

# Run linter
ruff check src/
```

## Coding Standards

### General Principles

All code must follow the 82 coding rules defined in `coding-rules.md`. Key principles:

1. **DRY (Don't Repeat Yourself)**: No code duplication
2. **SOLID Principles**: Single responsibility, dependency injection
3. **KISS (Keep It Simple)**: Simplest solution that works
4. **Type Safety**: Type hints on all functions
5. **Self-Documenting**: Code explains itself through structure

### Python Style

```python
# Good: Clear, typed, documented
def extract_entities(text: str, confidence_threshold: float = 0.7) -> list[Entity]:
    """
    Extract entities from text with confidence filtering.
    
    Args:
        text: Input text to process
        confidence_threshold: Minimum confidence score
        
    Returns:
        List of extracted entities above threshold
        
    Raises:
        ValueError: If text is empty
    """
    if not text:
        raise ValueError("Text cannot be empty")
    
    entities = self._perform_extraction(text)
    return self._filter_by_confidence(entities, confidence_threshold)

# Bad: No types, unclear, no docs
def extract(txt, thresh=0.7):
    if not txt:
        raise ValueError("empty")
    ents = self._extract(txt)
    return [e for e in ents if e.conf >= thresh]
```

### Function Size

- Maximum 20 lines per function
- One level of abstraction per function
- Extract helper functions for clarity

```python
# Good: Small, focused functions
def process_document(file_path: str) -> ProcessResult:
    """Process a document through the pipeline."""
    content = self._load_file(file_path)
    chunks = self._create_chunks(content)
    entities = self._extract_entities(chunks)
    return self._build_result(entities)

# Bad: Too long, multiple responsibilities
def process_document(file_path: str) -> ProcessResult:
    # 100+ lines of mixed loading, chunking, extraction...
```

### Documentation

```python
# Every public function needs a docstring
def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate semantic similarity between two texts.
    
    Uses sentence transformers to generate embeddings and
    computes cosine similarity.
    
    Args:
        text1: First text to compare
        text2: Second text to compare
        
    Returns:
        Similarity score between 0.0 and 1.0
        
    Example:
        >>> similarity = calculate_similarity("hello", "hi")
        >>> print(f"{similarity:.2f}")
        0.85
    """
    pass
```

### No Inline Comments

```python
# Good: Self-explanatory code
def is_valid_email(email: str) -> bool:
    """Check if email address is valid."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Bad: Needs comments to explain
def check(e):
    # Check if email matches pattern
    p = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  # Email regex
    return bool(re.match(p, e))  # Return True if valid
```

### Error Handling

```python
# Good: Specific exceptions with context
class EntityExtractionError(Exception):
    """Raised when entity extraction fails."""
    pass

def extract_entities(text: str) -> list[Entity]:
    """Extract entities from text."""
    if not text:
        raise ValueError(f"Cannot extract entities from empty text")
    
    try:
        entities = self.model.extract(text)
    except ModelError as e:
        raise EntityExtractionError(
            f"Failed to extract entities: {e}"
        ) from e
    
    return entities

# Bad: Generic exceptions, swallowed errors
def extract_entities(text):
    try:
        return self.model.extract(text)
    except:
        return []  # Silent failure
```

## Making Changes

### Branch Naming

```bash
# Feature branches
git checkout -b feature/add-entity-linking

# Bug fixes
git checkout -b fix/memory-leak-in-extraction

# Documentation
git checkout -b docs/update-deployment-guide
```

### Commit Messages

Follow conventional commits format:

```bash
# Format: <type>(<scope>): <description>

# Examples:
git commit -m "feat(extraction): add support for custom entity types"
git commit -m "fix(graph): resolve connection pool exhaustion"
git commit -m "docs(api): add examples for batch ingestion"
git commit -m "test(reasoning): add tests for query decomposition"
git commit -m "refactor(memory): simplify context management logic"
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

### Keep Changes Focused

- One feature or fix per pull request
- Maximum 400 lines changed per PR
- Split large changes into multiple PRs

## Testing

### Writing Tests

```python
# tests/test_extraction.py
import pytest
from scholaris.extraction.entities import EntityExtractor
from scholaris.types import Entity, EntityType

def test_entity_extraction_with_valid_text(config):
    """Test entity extraction returns entities for valid text."""
    extractor = EntityExtractor(config)
    text = "Machine learning is a subset of artificial intelligence."
    
    entities = extractor.extract_entities(text)
    
    assert isinstance(entities, list)
    assert len(entities) > 0
    assert all(isinstance(e, Entity) for e in entities)

def test_entity_extraction_with_empty_text_raises_error(config):
    """Test entity extraction raises ValueError for empty text."""
    extractor = EntityExtractor(config)
    
    with pytest.raises(ValueError, match="empty"):
        extractor.extract_entities("")

def test_entity_deduplication_removes_duplicates(config):
    """Test deduplication removes duplicate entities."""
    extractor = EntityExtractor(config)
    
    entities = [
        Entity(id="1", text="ML", type=EntityType.CONCEPT),
        Entity(id="2", text="ml", type=EntityType.CONCEPT),
    ]
    
    unique = extractor.deduplicate_entities(entities)
    
    assert len(unique) == 1
```

### Test Requirements

- Every new feature needs tests
- Bug fixes need regression tests
- Aim for 80%+ code coverage
- Tests must pass before PR approval

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_extraction.py

# Run specific test
pytest tests/test_extraction.py::test_entity_extraction_with_valid_text

# Run with coverage
pytest --cov=scholaris --cov-report=html

# Run with verbose output
pytest -v
```

## Submitting Changes

### Before Submitting

1. **Update from upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks:**
   ```bash
   # Format code
   black src/ tests/
   
   # Check types
   mypy src/
   
   # Run linter
   ruff check src/ tests/
   
   # Run tests
   pytest
   ```

3. **Update documentation:**
   - Update docstrings for changed functions
   - Update relevant markdown docs
   - Add examples if needed

### Creating Pull Request

1. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub:**
   - Use descriptive title
   - Fill out PR template completely
   - Link related issues
   - Add screenshots for UI changes

3. **PR Description Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Tests added/updated
   - [ ] All tests passing
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No new warnings
   
   ## Related Issues
   Fixes #123
   ```

## Review Process

### What Reviewers Look For

1. **Code Quality:**
   - Follows coding standards
   - Proper error handling
   - Type hints present
   - Well-documented

2. **Testing:**
   - Adequate test coverage
   - Tests are meaningful
   - Edge cases covered

3. **Design:**
   - Fits project architecture
   - Doesn't introduce coupling
   - Reusable and maintainable

### Addressing Feedback

```bash
# Make requested changes
git add .
git commit -m "refactor: address review feedback"

# Update PR
git push origin feature/your-feature-name
```

### Approval and Merge

- Requires approval from at least one maintainer
- All CI checks must pass
- No unresolved conversations
- Maintainers will merge when ready

## Development Workflow

### Typical Workflow

1. Find or create an issue
2. Fork and clone repository
3. Create feature branch
4. Make changes following standards
5. Write tests
6. Run all checks locally
7. Commit with conventional commits
8. Push and create PR
9. Address review feedback
10. Merge when approved

### Getting Help

- Comment on the issue
- Ask in GitHub Discussions
- Join community chat
- Tag maintainers if urgent

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README

Thank you for contributing to Scholaris!
