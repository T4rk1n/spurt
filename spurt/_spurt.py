import dash

from spurt.spurt_parser import parser_factory


class Spurt:
    def __init__(self,
                 name,
                 spurt,
                 component_libraries=None,
                 variables=None,):
        self.app = dash.Dash(name)
        self.parser = parser_factory(component_libraries, variables, self.app)
        self.app.layout = self.parser.parse(spurt).children[0]
