from flask import Flask, g
import settings_db

app = Flask(__name__)


def test_store_retrieve_cafe():
    settings_db.put_cafe_setting('joe', 'some cafe that joe likes')
    assert settings_db.get_cafe_setting('joe') == 'some cafe that joe likes'


def test_store_retrieve_price():
    settings_db.put_price_setting('joe', True)
    assert settings_db.get_price_setting('joe') == True


def test_uninitialized_cafe():
    assert settings_db.get_cafe_setting('jasmine') is None


def test_uninitialized_price():
    assert settings_db.get_price_setting('jasmine') is None


def test_overwrite():
    settings_db.put_cafe_setting('joe', 'some cafe we go to because jasmine likes it')
    assert settings_db.get_cafe_setting('joe') == 'some cafe we go to because jasmine likes it'
    settings_db.put_price_setting('joe', False)
    assert settings_db.get_price_setting('joe') == False


def test_second_context():
    assert settings_db.get_cafe_setting('joe') == 'some cafe we go to because jasmine likes it'
    assert settings_db.get_price_setting('joe') == False


with app.app_context():
    test_store_retrieve_cafe()
    test_store_retrieve_price()
    test_uninitialized_cafe()
    test_uninitialized_price()
    test_overwrite()


with app.app_context():
    test_second_context()

