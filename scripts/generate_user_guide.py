#noqa: INP001
import re
from pathlib import Path

from src import app_version
from src.docs.md_to_pdf_converter import MarkdownToPDFConverter


def remove_badges_block(md_content: str) -> str:
    """
    Remove all badge images from the Markdown content.

    This function identifies and removes all Markdown-formatted badge images from the input text.
    Badges in Markdown are typically formatted in two ways:

    1. Direct image syntax:
       ```
       ![Badge Label](https://badge-url.com)
       ```
    2. Hyperlinked image syntax:
       ```
       [![Badge Label](https://badge-url.com)](https://target-url.com)
       ```

    The function ensures that any badge lines are removed while preserving the rest of the document structure.

    Args:
    ----
        md_content (str): The Markdown content from which badge images should be removed.

    Returns:
    -------
        str: The modified Markdown content with all badges removed.

    """
    md_content = re.sub(r"!\[.*?]\(https?://.*?\)\n?", "", md_content)
    md_content = re.sub(r"\[!\[.*?]\(https?://.*?\)]\(https?://.*?\)\n?", "", md_content)
    return md_content # noqa: RET504


def remove_section(content: str, section_name: str, include_subsections: bool = False) -> str: # noqa: FBT001, FBT002
    """
    Remove the specified section and optionally its subsections from Markdown content.

    Arguments:
    ---------
        content (str): The original Markdown content
        section_name (str): The name of the section to remove
        include_subsections (bool): Whether to remove subsections

    Returns:
    -------
        str: Modified Markdown content with the specified section removed

    """
    # Escape special regex characters in the section name
    escaped_section = re.escape(section_name)
    # Create a pattern to search for headers of different levels (#, ##, ###, etc.)
    header_pattern = r"^(#{1,6})\s+" + escaped_section + r"\s*$"
    # Split the content into lines
    content_lines = content.split("\n")
    section_start = None
    section_level = None
    # Find the starting position and level of the target section header
    for i, line in enumerate(content_lines):
        match = re.match(header_pattern, line, re.MULTILINE)
        if match:
            section_start = i
            section_level = len(match.group(1))
            break
    if section_start is None: # Section not found
        return content
    # Find the end of the section
    section_end = len(content_lines)
    for i in range(section_start + 1, len(content_lines)):
        line = content_lines[i]
        # Check for the next header
        header_match = re.match(r"^(#{1,6})\s+", line)
        if header_match:
            current_level = len(header_match.group(1))
            # If include_subsections=False, stop at any header of the same or higher level
            # If include_subsections=True, stop only at headers of the same or higher level
            if (not include_subsections and current_level >= section_level) or \
                    (include_subsections and current_level <= section_level):
                section_end = i
                break
    # Remove the section
    modified_content = "\n".join(content_lines[:section_start] + content_lines[section_end:])
    # Clean up multiple consecutive empty lines
    modified_content = re.sub(r"\n{3,}", "\n\n", modified_content)
    return modified_content.strip()


def add_app_version_in_header(md_content: str) -> str:
    """Append the application version to the main header."""
    return md_content.replace("# Dehancer CLI", f"# Dehancer CLI {app_version}")


def remove_developer_mode_section(md_content: str) -> str:
    """Remove the 'Developer mode' section from the footer."""
    return remove_section(md_content, "Developer mode")


def remove_license_section(md_content: str) -> str:
    """Remove the 'License' section from the footer."""
    return remove_section(md_content, "License")


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    converter = MarkdownToPDFConverter(
        input_file_path=str(project_root / "README.md"),
        output_file_path=str(project_root / "docs/user-guide.pdf"),
        output_file_height=650,
        base_url=project_root,
        transformations=[remove_badges_block,
                         add_app_version_in_header,
                         remove_developer_mode_section,
                         remove_license_section],
    )
    converter.generate_pdf()
