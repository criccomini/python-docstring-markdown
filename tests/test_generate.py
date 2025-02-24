import difflib
import os
from pathlib import Path

import pytest

from python_docstring_markdown import crawl_package
from python_docstring_markdown.generate import MarkdownRenderer


@pytest.fixture(scope="session")
def test_dir():
    """Get the directory containing the test files."""
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="session")
def sample_package_dir(test_dir):
    """Get the path to the sample package."""
    return os.path.join(test_dir, "sample_package")


@pytest.fixture(scope="session")
def docs_file(test_dir):
    """Get the path to the documentation file."""
    return os.path.join(test_dir, "data/DOCUMENTATION.md")


@pytest.fixture(scope="session")
def generated_markdown(sample_package_dir):
    """Generate and load the documentation content."""
    # Creat a temporary file path
    import tempfile

    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_docs_file = Path(tmp_file.name)
        package = crawl_package(Path(sample_package_dir))
        renderer = MarkdownRenderer()
        renderer.render(package, tmp_docs_file)
        generated_markdown = tmp_docs_file.read_text(encoding="utf8")

    yield generated_markdown


def test_generated_markdown(generated_markdown, docs_file):
    """Compare generated markdown to expected content in data/DOCUMENTATION.md."""

    with open(docs_file, "r", encoding="utf8") as f:
        expected_content = f.read()

    if generated_markdown != expected_content:
        diff = list(
            difflib.ndiff(
                expected_content.splitlines(keepends=True),
                generated_markdown.splitlines(keepends=True),
            )
        )
        print("\n".join(diff))
        raise AssertionError("Generated markdown does not match expected content.")
