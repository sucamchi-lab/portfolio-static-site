import os
import sys
import shutil
import re
from textnode import TextNode, TextType, markdown_to_html_node, markdown_to_blocks, block_to_block_type, BlockType


def copy_directory(source, destination):
    """
    Recursively copy all contents from source directory to destination directory.
    First deletes all contents of the destination directory to ensure a clean copy.
    """
    # Delete destination directory if it exists
    if os.path.exists(destination):
        shutil.rmtree(destination)

    # Create the destination directory
    os.makedirs(destination)

    # Copy all files and subdirectories recursively
    for item in os.listdir(source):
        source_path = os.path.join(source, item)
        destination_path = os.path.join(destination, item)

        if os.path.isdir(source_path):
            # Recursively copy subdirectories
            copy_directory(source_path, destination_path)
        else:
            # Copy individual files
            shutil.copy2(source_path, destination_path)


def extract_title(markdown):
    """Extract the first heading from markdown as the page title."""
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        if block_to_block_type(block) == BlockType.HEADING:
            # Remove the # characters and return the heading text
            return re.sub(r"^#+\s+", "", block)
    raise ValueError("No heading found in markdown")


def generate_page(content_path, template_path, destination_path, basepath="/"):
    """
    Generate an HTML page from markdown content and an HTML template.
    Replaces {{ Title }} and {{ Content }} in the template.
    Also replaces all root-relative paths with the configurable basepath.
    """
    print(f"Generating page from {content_path}")

    # Read the markdown content
    with open(content_path, "r") as f:
        markdown_content = f.read()

    # Read the template
    with open(template_path, "r") as f:
        template = f.read()

    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    content_html = html_node.to_html()

    # Extract title from markdown
    title = extract_title(markdown_content)

    # Replace placeholders in template
    page_html = template.replace("{{ Title }}", title)
    page_html = page_html.replace("{{ Content }}", content_html)

    # Replace root-relative paths with basepath
    page_html = page_html.replace('href="/', f'href="{basepath}')
    page_html = page_html.replace('src="/', f'src="{basepath}')

    # Write to destination
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    with open(destination_path, "w") as f:
        f.write(page_html)

    print(f"Page generated at {destination_path}")


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath="/"):
    """
    Recursively generate HTML pages for all markdown files in the content directory.
    Maintains the same directory structure in the destination directory.
    """
    for item in os.listdir(dir_path_content):
        item_path = os.path.join(dir_path_content, item)
        dest_item_path = os.path.join(dest_dir_path, item)

        if os.path.isdir(item_path):
            # Recursively process subdirectories
            generate_pages_recursive(
                item_path, template_path, dest_item_path, basepath)
        elif item.endswith(".md"):
            # Convert markdown file to HTML
            html_filename = item.replace(".md", ".html")
            html_dest_path = os.path.join(
                os.path.dirname(dest_item_path), html_filename)
            generate_page(item_path, template_path, html_dest_path, basepath)


def main():
    # Get basepath from CLI argument, default to "/"
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"

    node = TextNode("Hello, World!", TextType.TEXT)
    print(node)
    print(f"Building site with basepath: {basepath}")

    # Copy static files to docs directory
    source_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    destination_dir = os.path.join(os.path.dirname(__file__), "..", "docs")

    print(f"Copying from {source_dir} to {destination_dir}")
    copy_directory(source_dir, destination_dir)
    print("Copy complete!")

    # Generate HTML pages from all markdown files in content directory
    content_dir = os.path.join(os.path.dirname(__file__), "..", "content")
    template_path = os.path.join(
        os.path.dirname(__file__), "..", "template.html")
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")

    print(f"Generating pages from {content_dir}")
    generate_pages_recursive(content_dir, template_path, docs_dir, basepath)
    print("Page generation complete!")


main()
