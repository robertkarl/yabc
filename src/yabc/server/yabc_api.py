import flask
from flask import Blueprint

from yabc.server import sql_backend

yabc_api = Blueprint("yabc_api", __name__)
bp = yabc_api


@yabc_api.route("/yabc/v1/run_basis", methods=["POST"])
def run_basis():
    userid = flask.request.args.get("userid")
    backend = sql_backend.get_db()
    return backend.run_basis(userid)


@yabc_api.route("/yabc/v1/taxdocs", methods=["POST", "GET"])
def taxdoc_create():
    userid = flask.request.args.get("userid")
    if not userid:
        userid = flask.session['user_id']
        assert userid
    backend = sql_backend.get_db()
    if flask.request.method == 'GET':
        print("userid is {}".format(userid))
        return backend.taxdoc_list(userid)
    exchange = flask.request.args.get("exchange")
    submitted_stuff = flask.request.get_data()
    return backend.taxdoc_create(exchange, userid, submitted_stuff)


@yabc_api.route("/yabc/v1/transactions", methods=["POST"])
def transactions_create():
    userid = flask.request.args.get("userid")
    tx = flask.request.get_data()
    backend = sql_backend.get_db()
    return backend.add_tx(userid, tx)


@yabc_api.route("/yabc/v1/users/<userid>", methods=["GET"])
def user_read(userid):
    backend = sql_backend.get_db()
    return backend.user_read(userid)


@yabc_api.route("/yabc/v1/users", methods=["POST"])
def user_create():
    name = flask.request.args.get("username")
    backend = sql_backend.get_db()
    return backend.user_create(name)
