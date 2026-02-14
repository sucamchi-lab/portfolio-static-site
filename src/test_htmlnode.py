import unittest

from htmlnode import LeafNode, ParentNode


class TestLeafNode(unittest.TestCase):
    def test_to_html_without_tag(self):
        node = LeafNode(None, "raw")
        self.assertEqual(node.to_html(), "raw")

    def test_to_html_with_props(self):
        node = LeafNode("a", "link", {"href": "https://example.com"})
        self.assertEqual(
            node.to_html(), '<a href="https://example.com">link</a>')

    def test_to_html_without_value_raises(self):
        node = LeafNode("p", None)  # type: ignore
        with self.assertRaises(ValueError):
            node.to_html()


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(),
                         "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_props(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node], {"class": "box"})
        self.assertEqual(parent_node.to_html(),
                         '<div class="box"><span>child</span></div>')

    def test_to_html_without_tag_raises(self):
        parent_node = ParentNode(
            None, [LeafNode("span", "child")])  # type: ignore
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_to_html_without_children_raises(self):
        # pyright: ignore[reportArgumentType]
        parent_node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_to_html_with_empty_children(self):
        parent_node = ParentNode("div", [])
        self.assertEqual(parent_node.to_html(), "<div></div>")


if __name__ == "__main__":
    unittest.main()
