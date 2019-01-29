import lark
import dash_core_components
import dash_html_components


_component_map = {
    'html': dash_html_components,
    'dcc': dash_core_components,
}


def _key_value(_, k, v):
    return str(k), v


def _obj(_, *values):
    return {
        k: v for k, v in values
    }


def _arr(_, *values):
    return list(values)


@lark.v_args(inline=True)
class ComponentTransformer(lark.Transformer):
    key_value = _key_value
    prop = _key_value
    obj = _obj
    props = _obj
    array = _arr
    children = _arr

    def __init__(self, component_libraries=None):
        self.component_libraries = {
            'html': dash_html_components,
            'dcc': dash_core_components,
        }
        self.component_libraries.update(component_libraries or {})

    def escape_string(self, value):
        return value.strip('"')

    def dotted_name(self, prefix, name):
        return str(prefix), str(name)

    def component(self, lib_component, *children_props):
        lib, name = lib_component
        module = _component_map.get(lib)
        component_cls = getattr(module, name)

        if len(children_props) == 2:
            # First are the children
            children = children_props[0]
            if not isinstance(children, list):
                children = [children]
            props = children_props[1]
        else:
            children = []
            props = children_props[0]

        if isinstance(props, tuple):
            # If there's only one prop it will be a tuple but we need dict.
            props = {props[0]: props[1]}

        return component_cls(children, **props)


def parser_factory(component_libraries=None):
    return lark.Lark.open(
        'spurt.lark',
        rel_to=__file__,
        parser='lalr',
        transformer=ComponentTransformer(component_libraries)
    )

