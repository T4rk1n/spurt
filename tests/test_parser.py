import dash_html_components as html
from spurt.spurt_parser import parser_factory


def test_parse_component():
    parser = parser_factory(
        variables={
            'bg_color': 'purple'
        }
    )
    tree = parser.parse('''
    <html.Div
        (
            "children"
            <html.Div
                ("children 2") 
                id="nested-child"
                style={backgroundColor: $bg_color}
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
    assert nested.style['backgroundColor'] == 'purple'
