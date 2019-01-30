import time

from spurt import Spurt

from pytest_dash.utils import wait_for_text_to_equal


def test_spurt_app(dash_threaded, selenium):
    s = '''
    <html.Div
        (
            <dcc.Input id="input">
            <html.Div
                id="output"
                children=(@input.value) => @input.value
            >
        )
    >
    '''
    app = Spurt(__name__, s)
    dash_threaded(app.app)
    _input = selenium.find_element_by_id('input')
    _input.send_keys('Hello spurt')
    wait_for_text_to_equal(selenium, '#output', 'Hello spurt')
