import dash_html_components as html
from spurt.spurt_parser import parser_factory

parser = parser_factory()


def test_parse_component():
    tree = parser.parse('''
    <html.Div 
        (
            "children"
            <html.Div 
                ("children 2") 
                id="nested-child"
                style={backgroundColor: "purple"}
            >
        )
        id="test"
    >
    ''')
    div = tree.children[0]

    assert isinstance(div, html.Div)
    assert div.id == 'test'
    assert len(div.children) == 2

    nested = div.children[1]

    assert nested.id == "nested-child"
    assert 'backgroundColor' in nested.style

