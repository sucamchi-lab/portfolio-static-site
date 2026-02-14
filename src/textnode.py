import re
from enum import Enum

from htmlnode import LeafNode, ParentNode


class TextType(Enum):
    TEXT = "text"
    LINKS = "link"
    LINK = "link"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    IMAGE = "image"


class BlockType(Enum):
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    PARAGRAPH = "paragraph"


class TextNode():
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if isinstance(other, TextNode):
            return self.text == other.text and self.text_type == other.text_type and self.url == other.url
        return False

    def __repr__(self):
        return f"TextNode(text='{self.text}', text_type='{self.text_type}', url='{self.url}')"


def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    if text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    if text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    if text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    if text_node.text_type in (TextType.LINKS, getattr(TextType, "LINK", None)):
        return LeafNode("a", text_node.text, {"href": text_node.url})
    if text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    raise ValueError(f"Unsupported text type: {text_node.text_type}")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        segments = node.text.split(delimiter)
        if len(segments) % 2 == 0:
            raise ValueError("Unmatched delimiter")
        for index, segment in enumerate(segments):
            if segment == "":
                continue
            if index % 2 == 0:
                new_nodes.append(TextNode(segment, TextType.TEXT))
            else:
                new_nodes.append(TextNode(segment, text_type))
    return new_nodes


def extract_markdown_images(text):
    return re.findall(r"!\[(.*?)\]\((.*?)\)", text)


def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[(.*?)\]\((.*?)\)", text)


def split_nodes_image(old_nodes):
    new_nodes = []
    pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        matches = list(pattern.finditer(node.text))
        if not matches:
            new_nodes.append(node)
            continue
        last_index = 0
        for match in matches:
            if match.start() > last_index:
                new_nodes.append(
                    TextNode(node.text[last_index:match.start()], TextType.TEXT))
            alt_text, url = match.group(1), match.group(2)
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            last_index = match.end()
        if last_index < len(node.text):
            new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    pattern = re.compile(r"(?<!!)\[(.*?)\]\((.*?)\)")
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        matches = list(pattern.finditer(node.text))
        if not matches:
            new_nodes.append(node)
            continue
        last_index = 0
        for match in matches:
            if match.start() > last_index:
                new_nodes.append(
                    TextNode(node.text[last_index:match.start()], TextType.TEXT))
            anchor_text, url = match.group(1), match.group(2)
            new_nodes.append(TextNode(anchor_text, TextType.LINK, url))
            last_index = match.end()
        if last_index < len(node.text):
            new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT))
    return new_nodes


def split_nodes_underscore(old_nodes):
    """Split nodes on underscore delimiters using regex to avoid word-internal underscores."""
    new_nodes = []
    pattern = re.compile(r"_([^_]+?)_")
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        matches = list(pattern.finditer(node.text))
        if not matches:
            new_nodes.append(node)
            continue
        last_index = 0
        for match in matches:
            if match.start() > last_index:
                new_nodes.append(
                    TextNode(node.text[last_index:match.start()], TextType.TEXT))
            content = match.group(1)
            new_nodes.append(TextNode(content, TextType.ITALIC))
            last_index = match.end()
        if last_index < len(node.text):
            new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT))
    return new_nodes


def split_nodes_asterisk(old_nodes):
    """Split nodes on asterisk delimiters using regex."""
    new_nodes = []
    pattern = re.compile(r"\*([^\*]+?)\*")
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        matches = list(pattern.finditer(node.text))
        if not matches:
            new_nodes.append(node)
            continue
        last_index = 0
        for match in matches:
            if match.start() > last_index:
                new_nodes.append(
                    TextNode(node.text[last_index:match.start()], TextType.TEXT))
            content = match.group(1)
            new_nodes.append(TextNode(content, TextType.ITALIC))
            last_index = match.end()
        if last_index < len(node.text):
            new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT))
    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "__", TextType.BOLD)
    nodes = split_nodes_underscore(nodes)
    nodes = split_nodes_asterisk(nodes)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    return nodes


def markdown_to_blocks(markdown):
    blocks = re.split(r"\n\s*\n", markdown.strip())
    return [block.strip() for block in blocks if block.strip()]


def block_to_block_type(block):
    if re.match(r"^#{1,6} ", block):
        return BlockType.HEADING
    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE

    lines = block.split("\n")
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    ordered = True
    for index, line in enumerate(lines, start=1):
        if not line.startswith(f"{index}. "):
            ordered = False
            break
    if ordered:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def text_to_children(text):
    return [text_node_to_html_node(node) for node in text_to_textnodes(text)]


def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == BlockType.HEADING:
        level = len(block.split(" ", 1)[0])
        text = block[level + 1:]
        return ParentNode(f"h{level}", text_to_children(text))
    if block_type == BlockType.CODE:
        lines = block.split("\n")
        code_text = "\n".join(lines[1:-1])
        return ParentNode("pre", [LeafNode("code", code_text)])
    if block_type == BlockType.QUOTE:
        lines = block.split("\n")
        cleaned = [line[2:] if line.startswith(
            "> ") else line[1:] for line in lines]
        return ParentNode("blockquote", text_to_children("\n".join(cleaned)))
    if block_type == BlockType.UNORDERED_LIST:
        items = []
        for line in block.split("\n"):
            items.append(ParentNode("li", text_to_children(line[2:])))
        return ParentNode("ul", items)
    if block_type == BlockType.ORDERED_LIST:
        items = []
        for index, line in enumerate(block.split("\n"), start=1):
            items.append(ParentNode(
                "li", text_to_children(line[len(f"{index}. "):])))
        return ParentNode("ol", items)
    return ParentNode("p", text_to_children(block))


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = [block_to_html_node(block) for block in blocks]
    return ParentNode("div", children)
