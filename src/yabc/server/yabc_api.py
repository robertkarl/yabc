import functools
import os

import flask
from flask import Blueprint

from yabc.server import sql_backend

yabc_api = Blueprint("yabc_api", __name__)
bp = yabc_api


def is_authorized(userid):
    """ @param userid: needs to match the logged in user. """
    print("checking on user {}".format(userid))
    FLASK_ENV_KEY = "FLASK_ENV"
    env = os.environ.get(FLASK_ENV_KEY)
    if env == "development":
        # Anything goes in development.
        return True
    if not flask.g.user:
        return False
    if flask.g.user.userid == userid:
        return True
    return False


def check_authorized(view):
    """
    Check the userid attached to the request against the logged-in user.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        userid = flask.request.args.get("userid")
        if not userid:
            userid = flask.session["user_id"]
        assert userid
        if not is_authorized(userid):
            return flask.make_response(("", 500))
        return view(**kwargs)

    return wrapped_view

def get_userid():
    userid = flask.request.args.get("userid")
    if not userid:
        userid = flask.session["user_id"]
    assert userid
    return userid


@yabc_api.route("/yabc/v1/run_basis", methods=["POST"])
@check_authorized
def run_basis():
    """
    Perform the cost basis calculations and write them all to the database.
    """
    userid = get_userid()
    backend = sql_backend.get_db()
    result = backend.run_basis(userid)
    return result


@check_authorized
@yabc_api.route("/yabc/v1/taxdocs", methods=["POST", "GET"])
def taxdocs():
    if "userid" in flask.request.values:
        userid = flask.request.values["userid"]
    else:
        userid = flask.session["user_id"]
    assert userid
    backend = sql_backend.get_db()
    if flask.request.method == "GET":
        return backend.taxdoc_list(userid)
    exchange = flask.request.values["exchange"]
    submitted_file = flask.request.files["taxdoc"]
    return backend.taxdoc_create(exchange, userid, submitted_file)


@check_authorized
@yabc_api.route("/yabc/v1/transactions/<txid>", methods=["DELETE"])
def transaction_update(txid):
    if "userid" in flask.request.values:
        userid = flask.request.values["userid"]
    else:
        userid = flask.session["user_id"]
    assert userid
    backend = sql_backend.get_db()
    if flask.request.method == "DELETE":
        backend.tx_delete(userid, txid)
    elif flask.request.method == "PUT":
        backend.tx_update(userid, txid, request.values)
    else:
        raise ValueError(
            "method {} not support for transaction".format(flask.request.method)
        )
    sql_backend.close_db()
    return flask.jsonify({"result": "Deleted transaction with id {}".format(txid)})


@check_authorized
@yabc_api.route("/yabc/v1/transactions", methods=["GET", "POST"])
def transactions():
    if "userid" in flask.request.values:
        userid = flask.request.values["userid"]
    else:
        userid = flask.session["user_id"]
    assert userid
    backend = sql_backend.get_db()
    if flask.request.method == "GET":
        return backend.tx_list(userid)
    tx = flask.request.values["tx"]
    assert tx
    return backend.add_tx(userid, tx)


@check_authorized
@yabc_api.route("/yabc/v1/users/<userid>", methods=["GET"])
def user_read(userid):
    backend = sql_backend.get_db()
    return backend.user_read(userid)


@yabc_api.route("/yabc/v1/users", methods=["POST"])
def user_create():
    name = flask.request.args.get("username")
    backend = sql_backend.get_db()
    return backend.user_create(name)
