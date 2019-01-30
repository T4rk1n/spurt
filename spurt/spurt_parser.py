import lark
import dash_core_components
import dash_html_components
from dash.dependencies import Output, Input, State


def _key_value(_, k, v):
    return str(k), v


def _obj(_, *values):
    return {
        k: v for k, v in values
    }


def _arr(_, *values):
    return list(values)


class Callback:
    def __init__(self, inputs, output, states=None):
        self.inputs = inputs
        if isinstance(self.inputs, CallbackInput):
            self.inputs = [self.inputs]
        self.states = states or []
        if isinstance(self.states, CallbackState):
            self.states = [self.states]
        self.output = output
        self.output_prop = None

    def __call__(self, *args):
        # TODO analyze args and map inputs to output
        output = self.output
        # TODO make more dry
        if isinstance(self.output, CallbackInput):
            index = self.inputs.index(self.output)
            output = args[index]
        elif isinstance(self.output, CallbackState):
            index = self.states.index(self.output)
            output = args[len(self.inputs):][index]
        return output

    def callback(self, app, output_id):
        inputs = [x.get_dash_instance() for x in self.inputs]
        states = [x.get_dash_instance() for x in self.states]
        app.callback(Output(output_id, self.output_prop), inputs, states)(self)


class CallbackItem:
    _callback_class = None

    def __init__(self, component_id, component_prop):
        self.component_id = component_id
        self.component_prop = component_prop

    def get_dash_instance(self):
        return self._callback_class(self.component_id, self.component_prop)

    def __eq__(self, other):
        if not isinstance(other, CallbackItem):
            return False
        return (
                self._callback_class == other._callback_class
                and self.component_id == other.component_id
                and self.component_prop == other.component_prop
        )

    def __hash__(self):
        return hash((
            self._callback_class,
            self.component_id,
            self.component_prop
        ))


class CallbackInput(CallbackItem):
    _callback_class = Input


class CallbackState(CallbackItem):
    _callback_class = State


class CallbackBody:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass


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

    def callback(self, inputs, output, *args):
        states = None
        if args:
            output = args[-1]
            states = output
        return Callback(inputs, output, states)

    def prop(self, key, value):
        if isinstance(value, Callback):
            value.output_prop = key
        return str(key), value

    def callback_input(self, dotted_name):
        return CallbackInput(*dotted_name)

    def callback_state(self, dotted_name):
        return CallbackState(*dotted_name)

    def callback_body(self, *body):
        return body

    def operation(self, v1, op, v2):
        if op.data == 'add':
            return lambda: v1 + v2
        if op.data == 'mul':
            return lambda: v1 * v2
        if op.data == 'div':
            return lambda: v1 / v2
        if op.data == 'sub':
            return lambda: v1 - v2


def parser_factory(component_libraries=None, variables=None, app=None):
    return lark.Lark.open(
        'spurt.lark',
        rel_to=__file__,
        parser='lalr',
        transformer=ComponentTransformer(
            component_libraries, variables, app
        )
    )

