import unittest

from textnode import (
    BlockType,
    TextNode,
    TextType,
    block_to_block_type,
    extract_markdown_images,
    extract_markdown_links,
    markdown_to_html_node,
    markdown_to_blocks,
    split_nodes_image,
    split_nodes_link,
    split_nodes_delimiter,
    text_to_textnodes,
    text_node_to_html_node,
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode("Click here", TextType.LINKS, "https://example.com")
        node2 = TextNode("Click here", TextType.LINKS, "https://example.com")
        self.assertEqual(node, node2)

    def test_not_eq_different_text(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("Different text", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_eq_different_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_not_eq_different_url(self):
        node = TextNode("Click here", TextType.LINKS, "https://example.com")
        node2 = TextNode("Click here", TextType.LINKS, "https://different.com")
        self.assertNotEqual(node, node2)

    def test_not_eq_url_none_vs_url(self):
        node = TextNode("Click here", TextType.LINKS)
        node2 = TextNode("Click here", TextType.LINKS, "https://example.com")
        self.assertNotEqual(node, node2)


class TestTextNodeToHtmlNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("hello", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "hello")

    def test_bold(self):
        node = TextNode("bold", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "bold")

    def test_italic(self):
        node = TextNode("italic", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "italic")

    def test_code(self):
        node = TextNode("code", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "code")

    def test_link(self):
        node = TextNode("link", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "link")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    def test_image(self):
        node = TextNode("alt", TextType.IMAGE, "https://example.com/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props,
            {"src": "https://example.com/image.png", "alt": "alt"},
        )

    def test_invalid_text_type(self):
        node = TextNode("oops", "bad-type")
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_bold(self):
        nodes = [TextNode("This is **bold** text", TextType.TEXT)]
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(split_nodes_delimiter(
            nodes, "**", TextType.BOLD), expected)

    def test_split_multiple_code(self):
        nodes = [TextNode("A `code` and `more`", TextType.TEXT)]
        expected = [
            TextNode("A ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("more", TextType.CODE),
        ]
        self.assertEqual(split_nodes_delimiter(
            nodes, "`", TextType.CODE), expected)

    def test_split_ignores_non_text(self):
        nodes = [
            TextNode("bold", TextType.BOLD),
            TextNode("plain", TextType.TEXT),
        ]
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode("plain", TextType.TEXT),
        ]
        self.assertEqual(split_nodes_delimiter(
            nodes, "**", TextType.BOLD), expected)

    def test_split_unmatched_delimiter_raises(self):
        nodes = [TextNode("This is **bold text", TextType.TEXT)]
        with self.assertRaises(ValueError):
            split_nodes_delimiter(nodes, "**", TextType.BOLD)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_images(self):
        text = "Text ![alt](https://example.com/img.png) and ![logo](logo.jpg)"
        self.assertEqual(
            extract_markdown_images(text),
            [("alt", "https://example.com/img.png"), ("logo", "logo.jpg")],
        )

    def test_extract_images_none(self):
        text = "No images here"
        self.assertEqual(extract_markdown_images(text), [])


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_links(self):
        text = "A [link](https://example.com) and [docs](docs.html)"
        self.assertEqual(
            extract_markdown_links(text),
            [("link", "https://example.com"), ("docs", "docs.html")],
        )

    def test_extract_links_ignores_images(self):
        text = "![alt](https://example.com/img.png) and [link](https://example.com)"
        self.assertEqual(
            extract_markdown_links(text),
            [("link", "https://example.com")],
        )

    def test_extract_links_none(self):
        text = "No links here"
        self.assertEqual(extract_markdown_links(text), [])


class TestSplitNodesImage(unittest.TestCase):
    def test_split_single_image(self):
        nodes = [TextNode("Text ![alt](url.png) end", TextType.TEXT)]
        expected = [
            TextNode("Text ", TextType.TEXT),
            TextNode("alt", TextType.IMAGE, "url.png"),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertEqual(split_nodes_image(nodes), expected)

    def test_split_multiple_images(self):
        nodes = [TextNode("![a](a.png) and ![b](b.jpg)", TextType.TEXT)]
        expected = [
            TextNode("a", TextType.IMAGE, "a.png"),
            TextNode(" and ", TextType.TEXT),
            TextNode("b", TextType.IMAGE, "b.jpg"),
        ]
        self.assertEqual(split_nodes_image(nodes), expected)

    def test_split_images_ignores_non_text(self):
        nodes = [TextNode("bold", TextType.BOLD)]
        self.assertEqual(split_nodes_image(nodes), nodes)


class TestSplitNodesLink(unittest.TestCase):
    def test_split_single_link(self):
        nodes = [
            TextNode("Text [link](https://example.com) end", TextType.TEXT)]
        expected = [
            TextNode("Text ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertEqual(split_nodes_link(nodes), expected)

    def test_split_multiple_links(self):
        nodes = [TextNode("[a](a.html) and [b](b.html)", TextType.TEXT)]
        expected = [
            TextNode("a", TextType.LINK, "a.html"),
            TextNode(" and ", TextType.TEXT),
            TextNode("b", TextType.LINK, "b.html"),
        ]
        self.assertEqual(split_nodes_link(nodes), expected)

    def test_split_links_ignore_images(self):
        nodes = [TextNode("![alt](img.png) and [link](url)", TextType.TEXT)]
        expected = [
            TextNode("![alt](img.png) and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "url"),
        ]
        self.assertEqual(split_nodes_link(nodes), expected)

    def test_split_links_ignores_non_text(self):
        nodes = [TextNode("code", TextType.CODE)]
        self.assertEqual(split_nodes_link(nodes), nodes)


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes_all_types(self):
        text = (
            "This is **text** with an *italic* word and a `code block` "
            "and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) "
            "and a [link](https://boot.dev)"
        )
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE,
                     "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(text_to_textnodes(text), expected)

    def test_text_to_textnodes_plain_text(self):
        text = "Just plain text"
        self.assertEqual(text_to_textnodes(text), [
                         TextNode(text, TextType.TEXT)])


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        markdown = """# Heading

Paragraph one.

Paragraph two with
two lines.

* list item 1
* list item 2
"""
        expected = [
            "# Heading",
            "Paragraph one.",
            "Paragraph two with\ntwo lines.",
            "* list item 1\n* list item 2",
        ]
        self.assertEqual(markdown_to_blocks(markdown), expected)

    def test_markdown_to_blocks_trims_and_skips_empty(self):
        markdown = """

  First block  


Second block

"""
        self.assertEqual(markdown_to_blocks(markdown), [
                         "First block", "Second block"])


class TestBlockToBlockType(unittest.TestCase):
    def test_heading_block(self):
        block = "### Heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_code_block(self):
        block = "```\nprint('hi')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_quote_block(self):
        block = "> Quote line\n> Another"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_unordered_list_block(self):
        block = "- item 1\n- item 2"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_ordered_list_block(self):
        block = "1. first\n2. second\n3. third"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_paragraph_block(self):
        block = "Just a paragraph with text."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_invalid_sequence(self):
        block = "1. first\n3. third"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_markdown_to_html_node(self):
        markdown = """# Heading

Paragraph with **bold** and *italic*.

> Quote line
> Next line

- item 1
- item 2

1. first
2. second

```
code
```
"""
        expected = (
            "<div>"
            "<h1>Heading</h1>"
            "<p>Paragraph with <b>bold</b> and <i>italic</i>.</p>"
            "<blockquote>Quote line\nNext line</blockquote>"
            "<ul><li>item 1</li><li>item 2</li></ul>"
            "<ol><li>first</li><li>second</li></ol>"
            "<pre><code>code</code></pre>"
            "</div>"
        )
        self.assertEqual(markdown_to_html_node(markdown).to_html(), expected)


if __name__ == "__main__":
    unittest.main()
