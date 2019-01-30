from spurt import Spurt

s = '''
<html.Div
    (
        <html.H2 ("Spurt test")>
        <dcc.Input id="input">
        <html.Div
            id="output"
            # `@` for Input, the value is from callback argument
            children=(@input.value) => "You said: " + @input.value
        >
    )
>
'''
spurt_app = Spurt(__name__, s)
app = spurt_app.app

