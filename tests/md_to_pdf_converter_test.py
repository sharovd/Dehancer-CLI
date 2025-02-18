from __future__ import annotations

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from pytest import param as test_data  # noqa: PT013

from src.docs.md_to_pdf_converter import MarkdownToPDFConverter


@pytest.mark.unit
@pytest.mark.parametrize(("md_content", "expected_result"), [
    test_data("# Header\nContent", "# Header\nContent",
              id="Simple markdown content"),
    test_data("*italic* **bold**\n- list item", "*italic* **bold**\n- list item",
              id="Markdown with formatting"),
    test_data("", "",
              id="Empty content"),
])
def test_read_markdown_file_returns_content(md_content: str, expected_result: str):
    # Arrange: create mock file and converter instance
    with patch("pathlib.Path.open", mock_open(read_data=md_content)):
        converter = MarkdownToPDFConverter("input.md", "output.pdf", 300, Path(), None)
        # Act: perform method under test
        actual_result = converter.read_markdown_file()
        # Assert
        assert actual_result == expected_result


@pytest.mark.unit
@pytest.mark.parametrize(("md_content", "transformations", "expected_result"), [
    test_data("# Test", [lambda x: x.lower()], "# test",
              id="Single transformation"),
    test_data("# Test", [lambda x: x.lower(), lambda x: x.replace("test", "example")], "# example",
              id="Multiple transformations"),
    test_data("# Test", None, "# Test",
              id="No transformations"),
    test_data("", [lambda x: x.upper()], "",
              id="Empty content with transformation"),
])
def test_transform_markdown_applies_transformations(md_content: str,
                                                    transformations: list[callable] | None, expected_result: str):
    # Arrange: create converter instance
    converter = MarkdownToPDFConverter("input.md", "output.pdf", 300, Path(), transformations)
    # Act: perform method under test
    actual_result = converter.transform_markdown(md_content)
    # Assert
    assert actual_result == expected_result


@pytest.mark.unit
@pytest.mark.parametrize(("md_content", "expected_html"), [
    test_data("# Header", "<h1>Header</h1>\n",
              id="Simple header"),
    test_data("```python\ncode\n```", "<pre><code>code\n</code></pre>\n",
              id="Code block"),
    test_data("| A | B |\n|---|---|\n| 1 | 2 |",
              "<table>\n"
              "<thead>\n<tr>\n  <th>A</th>\n  <th>B</th>\n</tr>\n</thead>\n"
              "<tbody>\n<tr>\n  <td>1</td>\n  <td>2</td>\n</tr>\n</tbody>\n"
              "</table>\n",
              id="Table"),
    test_data("", "<p></p>\n",
              id="Empty content"),
])
def test_convert_to_html_returns_html_data(md_content: str, expected_html: str):
    # Act: perform method under test
    actual_html = MarkdownToPDFConverter.convert_to_html(md_content)
    # Assert
    assert actual_html == expected_html


@pytest.mark.unit
def test_get_css_returns_default_stylesheet():
    # Arrange: create converter instance
    converter = MarkdownToPDFConverter("input.md", "output.pdf", 450, Path(), None)
    # Act: perform method under test
    css = converter.get_css()
    # Assert: check that essential CSS properties are present
    assert "@page" in css
    assert "body" in css
    assert "table" in css
    assert "pre" in css
    assert "code" in css
    assert f"size: 210mm {converter.output_file_height}mm" in css


@pytest.mark.unit
def test_generate_pdf_creates_pdf_file():
    # Arrange: setup mocks and converter instance
    md_content = "# Test Document"
    with patch("pathlib.Path.open", mock_open(read_data=md_content)), \
            patch("pathlib.Path.exists") as mock_exists, \
            patch("pathlib.Path.mkdir") as mock_mkdir, \
            patch("weasyprint.HTML.write_pdf") as mock_write_pdf, \
            patch("builtins.print") as mock_print:
        mock_exists.return_value = False
        converter = MarkdownToPDFConverter("input.md", "output/test.pdf", 300, Path(), None)
        # Act: perform method under test
        converter.generate_pdf()
        # Assert: verify all the expected method calls
        mock_mkdir.assert_called_once()
        mock_write_pdf.assert_called_once_with("output/test.pdf")
        mock_print.assert_called_once_with("✅ PDF successfully created at output/test.pdf")
