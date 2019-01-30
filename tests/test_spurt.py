from pytest_dash.utils import wait_for_text_to_equal


def test_spurt_app(dash_subprocess):
    dash_subprocess('tests.apps.spurt_app')
    driver = dash_subprocess.driver
    _input = driver.find_element_by_id('input')
    _input.send_keys('Hello spurt')
    wait_for_text_to_equal(driver, '#output', 'Hello spurt')
