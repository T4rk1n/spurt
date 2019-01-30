import lark
import dash_core_components
import dash_html_components
from dash.dependencies import Output, Input


def _key_value(_, k, v):
    return str(k), v


def _obj(_, *values):
    return {
        k: v for k, v in values
    }


def _arr(_, *values):
    return list(values)


class Callback:
    def __init__(self, inputs, output):
        self.inputs = inputs
        self.output = output
        self.output_prop = None

    def __call__(self, *args):
        # TODO analyze args and map inputs to output
        return self.output

    def callback(self, app, output_id):
        inputs = [Input(*x) for x in self.inputs] \
            if isinstance(self.inputs, list) else [Input(*self.inputs)]
        app.callback(Output(output_id, self.output_prop), inputs)(self)


@lark.v_args(inline=True)
class ComponentTransformer(lark.Transformer):
    key_value = _key_value
    obj = _obj
    props = _obj
    array = _arr
    children = _arr

    def __init__(self, component_libraries=None, variables=None, app=None):
        self.component_libraries = {
            'html': dash_html_components,
            'dcc': dash_core_components,
        }
        self.component_libraries.update(component_libraries or {})
        self.variables = variables or {}
        self.app = app

    def variable(self, key):
        return self.variables.get(str(key).lstrip('$'))

    def escape_string(self, value):
        return value.strip('"')

    def dotted_name(self, prefix, name):
        return str(prefix), str(name)

    def component(self, lib_component, *children_props):
        lib, name = lib_component
        module = self.component_libraries.get(lib)
        component_cls = getattr(module, name)
        children = []

        if len(children_props) == 2:
            # First are the children
            children = children_props[0]
            if not isinstance(children, list):
                children = [children]
            props = children_props[1]
        else:
            props = children_props[0]

        if isinstance(props, tuple):
            # If there's only one prop it will be a tuple but we need dict.
            props = {props[0]: props[1]}

        if children:
            props['children'] = children

        _callbacks = []
        component_id = props.get('id')
        for k, v in props.items():
            if isinstance(v, Callback):

                _callbacks.append((k, v))

        for k, _ in _callbacks:
            del props[k]

        if self.app:
            @self.app.server.before_first_request
            def apply_callbacks():
                for _, callback in _callbacks:
                    callback.callback(self.app, component_id)

        return component_cls(**props)

    def callback(self, inputs, output):
        return Callback(inputs, output)

    def prop(self, key, value):
        if isinstance(value, Callback):
            value.output_prop = key
        return str(key), value


def parser_factory(component_libraries=None, variables=None, app=None):
    return lark.Lark.open(
        'spurt.lark',
        rel_to=__file__,
        parser='lalr',
        transformer=ComponentTransformer(
            component_libraries, variables, app
        )
    )

