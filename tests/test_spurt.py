import time

from spurt import Spurt


def test_spurt_app(dash_threaded):
    s = '''
    <html.Div
        (
            <dcc.Input id="input">
            <html.Div
                id="output"
                children=(input.value) => input.value
            >
        )
    >
    '''
    app = Spurt(__name__, s)
    dash_threaded(app.app)
    time.sleep(2)
