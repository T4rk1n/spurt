import dash_html_components as html
from spurt.spurt_parser import parser_factory

parser = parser_factory()


def test_parse_component():
    tree = parser.parse('<html.Div ("children" "children 2") id="test">')
    div = tree.children[0]
    assert isinstance(div, html.Div)
    assert div.id == 'test'
    assert len(div.children) == 2
