set dotenv-load := true

# Default recipe - list all available recipes
list:
    @just --list

# Run all tests with coverage reporting
test:
    uv run pytest -v --cov

# Run unit tests (excluding integration tests) with verbose output and fail-fast
test-unit:
    uv run pytest -m "not integration" -v --ff

# Run integration tests with verbose output and fail-fast
test-integration:
    uv run pytest -m "integration" -v --ff

# Run all tests in debug mode, stopping after the first failure and showing the full traceback
test-debug:
    uv run pytest -x --ff -v -m "not integration" && pytest -x --ff -v -m "integration"

# Run only the tests that failed in the previous test run, with verbose output and fail-fast
test-failed:
    uv run pytest --lf -x -v

# Analyze the codebase using cloc, excluding certain directories
cloc:
    @cloc . --vcs=git --exclude-dir=products,tests

# Build the package distribution
build:
    @echo "Building package..."
    uv build

# Publish the package to PyPI using UV, with the token provided in the environment variable
publish:
    @echo "Publishing package to PyPI..."
    uv publish --token $UV_PUBLISH_TOKEN
