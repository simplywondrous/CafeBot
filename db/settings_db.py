from flask import g
import sqlite3

# points to a sqlite3 db file (where database persistence is stored)
DATABASE = './user_settings.db'

# prepared statements for settings
GET_CAFE_SETTING = 'SELECT selected_cafe FROM CafeSettings WHERE user_id = ?'
PUT_CAFE_SETTING = 'REPLACE INTO CafeSettings VALUES (?, ?)'
GET_PRICE_SETTING = 'SELECT price_bool FROM PriceSettings WHERE user_id = ?'
PUT_PRICE_SETTING = 'REPLACE INTO PriceSettings VALUES (?, ?)'
GET_USER_IDS = 'SELECT user_id FROM PriceSettings'


"""
Must install sqlite3 on the host machine:
    sudo apt-get install sqlite3
Must generate the database once by running the init script:
    rm user_settings.db ; cat create_db.sql | sqlite3 user_settings.db
"""


def _get_db():
    """
    Call this to get a connection to the database.
    :return: sqlite3 database connection
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def _query_db(query, args=(), one=False):
    """
    Execute a query against the database connection from _get_db() and return the results as a list of named tuples.
    :param query: sql query to execute
    :param args: arguments for prepared statements
    :param one: set to True to only get a single (the first) result
    :return: list of namedTuples (or one named tuple if one is True)
    """
    con = _get_db()
    cur = con.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    con.commit()
    return (rv[0] if rv else None) if one else rv


def get_user_ids():
    """
    Get all user ids.
    :return: row of user ids
    """
    user_row = _query_db(GET_USER_IDS)

    if user_row is not None:
        return user_row[0]
    else:
        return None


def get_cafe_setting(user_id):
    """
    Lookup the cafe setting for the given user_id.
    :param user_id: string user identifier
    :return: name of selected cafe for this user
    """
    cafe_row = _query_db(GET_CAFE_SETTING, (user_id,), True)

    if cafe_row is not None:
        return cafe_row['selected_cafe']
    else:
        return None


def put_cafe_setting(user_id, selected_cafe):
    """
    Insert or replace the selected cafe for a given user.
    :param user_id: string user identifier
    :param selected_cafe: name of selected cafe for this user
    """
    _query_db(PUT_CAFE_SETTING, (user_id, selected_cafe))


def get_price_setting(user_id):
    """
    Lookup the price setting for the given user_id. (whether or not to show prices)
    :param user_id: string user identifier
    :return: current boolean setting value or None if not set
    """
    price_row = _query_db(GET_PRICE_SETTING, (user_id,), True)

    if price_row is not None:
        return price_row['price_bool'] != 0
    else:
        return None


def put_price_setting(user_id, price_bool):
    """
    Insert or replace the price boolean setting for a given user.
    :param user_id: string user identifier
    :param price_bool: new setting value
    """
    _query_db(PUT_PRICE_SETTING, (user_id, price_bool))
