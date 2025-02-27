from __future__ import annotations

from pathlib import Path
from typing import Callable

import markdown2
from weasyprint import HTML

from src.api.constants import ENCODING_UTF_8


class MarkdownToPDFConverter:
    """
    A converter that transforms a Markdown file into a styled PDF.

    This class reads a Markdown file, applies custom transformations, converts it to HTML using markdown2,
    injects custom CSS for styling, and then generates a PDF file using WeasyPrint.

    Attributes
    ----------
        input_file_path (str): The path to the input Markdown file.
        output_file_path (str): The path where the output PDF will be saved.
        output_file_height (int): The height of the output PDF.
        base_url (str): The base URL used to resolve relative asset paths for HTML.
        transformations (list[Callable[[str], str]] | None): A list of functions to transform the Markdown content.

    """

    def __init__(self, input_file_path: str, output_file_path: str,
                 output_file_height: int, base_url: Path,
                 transformations: list[Callable[[str], str]] | None) -> None:
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.output_file_height = output_file_height
        self.transformations = transformations or []
        self.base_url = base_url

    def read_markdown_file(self) -> str:
        """
        Read the Markdown file content.

        Returns
        -------
            str: The content of the Markdown file.

        """
        with Path(self.input_file_path).open("r", encoding=ENCODING_UTF_8) as f:
            return f.read()

    def transform_markdown(self, md_content: str) -> str:
        """
        Apply all provided transformations to the Markdown content.

        Each function in the self.transformations list is applied in sequence to the content.

        Args:
        ----
            md_content (str): The original Markdown content.

        Returns:
        -------
            str: The transformed Markdown content.

        """
        for transform in self.transformations:
            md_content = transform(md_content)
        return md_content

    @staticmethod
    def convert_to_html(md_content: str) -> str:
        """
        Convert the Markdown content to HTML.

        Uses markdown2 for conversion with support for tables and fenced code blocks.

        Args:
        ----
            md_content (str): The Markdown content.

        Returns:
        -------
            str: The converted HTML content.

        """
        return markdown2.markdown(md_content, extras=["tables", "fenced-code-blocks"])

    def get_css(self) -> str:
        """
        Get the CSS stylesheet for PDF formatting.

        This CSS defines page size, font and layout settings, table styles (including shaded header cells),
        image sizes, and code block and inline-code styling.

        Returns
        -------
            str: The CSS stylesheet.

        """
        grey_color = "#f5f5f5"

        return f"""
        @page {{
            /* One page with fixed dimensions */
            size: 210mm {self.output_file_height}mm;
            margin: 10mm;
        }}

        body {{
            font-family: Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.5;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}

        td, th {{
            border: 1px solid #ddd;
            padding: 8px;
            /* Smaller text in tables */
            font-size: 9pt;
        }}

        th {{
            background-color: {grey_color};
        }}

        /* Fix the size of logo images inside tables */
        table img.img-logo {{
            width: 60px;
            height: auto;
        }}

        /* Fix the size of screenshots images inside tables */
        table img.img-screenshot {{
            width: 450px;
            height: auto;
        }}

        /* Fix the size of screenshots images */
        img.img-screenshot {{
            width: 450px;
            height: auto;
            margin: 10px 0;
        }}

        /* Center images outside of tables */
        img {{
            display: block;
            margin: 10px auto;
        }}

        /* Styles for code blocks */
        pre {{
            background-color: {grey_color};
            padding: 10px;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 8pt;
            border-radius: 5px;
            font-family: Menlo, Consolas, "Courier New", monospace;
        }}

        /* Styles for inline code */
        code {{
            background-color: {grey_color};
            padding: 3px 5px;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 8pt;
            border-radius: 5px;
            font-family: Menlo, Consolas, "Courier New", monospace;
        }}
        """

    def generate_pdf(self) -> None:
        """
        Generate a PDF file from the Markdown file.

        The process involves:
          1. Reading and transforming the Markdown content.
          2. Converting the Markdown to HTML.
          3. Injecting CSS styles.
          4. Generating the PDF with WeasyPrint.
        """
        md_content = self.read_markdown_file()
        transformed_md = self.transform_markdown(md_content)
        html_content = self.convert_to_html(transformed_md)
        css = self.get_css()
        html_obj = HTML(
            string=f"<style>{css}</style>{html_content}",
            base_url=self.base_url,
        )
        output_dir = Path(self.output_file_path).parent
        if output_dir and not Path(output_dir).exists():
            Path.mkdir(output_dir)
        html_obj.write_pdf(self.output_file_path)
        print(f"✅ PDF successfully created at {self.output_file_path}")  # noqa: T201
