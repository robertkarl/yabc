import functools
import os

import flask
from flask import Blueprint

from yabc import user
from yabc.server import sql_backend
from yabc.user import User

yabc_api = Blueprint("yabc_api", __name__)
bp = yabc_api
USER_ID_KEY = "user_id"


def is_authorized(userid):
    """ @param userid: needs to match the logged in user. """
    FLASK_ENV_KEY = "FLASK_ENV"
    env = os.environ.get(FLASK_ENV_KEY)
    if env == "development":
        # Anything goes in development.
        return True
    if not flask.g.user:
        return False
    assert isinstance(flask.g.user, user.User)
    if flask.g.user.id == userid:
        return True
    return False


def check_authorized(view):
    """
    Check the userid attached to the request against the logged-in user.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        userid = flask.request.args.get(USER_ID_KEY)
        if not userid:
            userid = flask.session.get(USER_ID_KEY)
        if not userid:
            raise RuntimeError("No userid, not authorized")
        if not is_authorized(userid):
            return flask.make_response(("", 500))
        return view(**kwargs)

    return wrapped_view


def get_userid():
    userid = flask.request.args.get(USER_ID_KEY)
    if not userid:
        userid = flask.session.get(USER_ID_KEY)
    if not userid:
        raise RuntimeError("User is not logged in. get_userid() failed.")
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


@yabc_api.route("/yabc/v1/download_8949/<taxyear>", methods=["GET"])
@check_authorized
def download_8949(taxyear):
    """
    Get the relevant tax document for a given year.
    """
    userid = get_userid()
    backend = sql_backend.get_db()
    user = backend.session.query(User).filter_by(id=userid).first()
    of = backend.download_8949(userid, int(taxyear))
    result = flask.send_file(
        of,
        mimetype="text/csv",
        cache_timeout=1,
        attachment_filename="{}-{}-8949.csv".format(user.username, taxyear),
        as_attachment=True,
    )
    return result


@yabc_api.route("/yabc/v1/taxdocs", methods=["POST", "GET"])
@check_authorized
def taxdocs():
    userid = get_userid()
    backend = sql_backend.get_db()
    if flask.request.method == "GET":
        return backend.taxdoc_list(userid)
    submitted_file = flask.request.files["taxdoc"]
    return backend.import_transaction_document(userid, submitted_file)


@yabc_api.route("/yabc/v1/transactions/by-exchange/<exchange_name>", methods=["DELETE"])
@check_authorized
def delete_by_exchange(exchange_name):
    userid = get_userid()
    try:
        deleted_rows = sql_backend.get_db().tx_delete_by_exchange(userid, exchange_name)
        sql_backend.close_db()
    except RuntimeError:
        return flask.make_response(("Failed to delete.", 500))
    return flask.jsonify(
        {
            "count": deleted_rows,
            "result": "Deleted transactions for exchange {}".format(exchange_name),
        }
    )


@yabc_api.route("/yabc/v1/transactions/<txid>", methods=["DELETE"])
@check_authorized
def transaction_update(txid):
    userid = get_userid()
    backend = sql_backend.get_db()
    if flask.request.method == "DELETE":
        backend.tx_delete(userid, txid)
    elif flask.request.method == "PUT":
        backend.tx_update(userid, txid, flask.request.values)
    else:
        raise ValueError(
            "method {} not support for transaction".format(flask.request.method)
        )
    sql_backend.close_db()
    return flask.jsonify({"result": "Deleted transaction with id {}".format(txid)})


@yabc_api.route("/yabc/v1/transactions", methods=["GET", "POST", "DELETE"])
@check_authorized
def transactions():
    userid = get_userid()
    backend = sql_backend.get_db()
    if flask.request.method == "GET":
        return backend.tx_list(userid)
    elif flask.request.method == "DELETE":
        return backend.transactions_clear_all(userid)
    tx = flask.request.values["tx"]
    assert tx
    return backend.add_tx(userid, tx)


@yabc_api.route("/yabc/v1/users/<userid>", methods=["GET"])
@check_authorized
def user_read(userid):
    backend = sql_backend.get_db()
    return backend.user_read(userid)


@yabc_api.route("/yabc/v1/users", methods=["POST"])
def user_create():
    name = flask.request.args.get("username")
    backend = sql_backend.get_db()
    return backend.user_create(name)
