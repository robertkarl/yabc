import flask
from flask import Blueprint

from yabc.server import sql_backend

yabc_api = Blueprint("yabc_api", __name__)
bp = yabc_api


@yabc_api.route("/yabc/v1/run_basis/<tax_year>", methods=["POST"])
def run_basis(tax_year):
    """
    Perform the cost basis calculations for a given tax year.

    Returns a CSV in form 8949 format. Also has the side effect of locking the
    portfolio's cost basis in for the given year.

    Prerequisites:
        - the given tax year must be ONE of the following:
            - the first year with any sale in the database
            - OR the oldest unlocked year with any sale transactions.

    Side effects:
        - Locks the tax year given.
        - Saves the list of transactions still in the pool into the table
          'pool'. These transactions will provide the literal basis for sales
          in future tax years.
    """
    userid = flask.request.args.get("userid")
    if not userid:
        userid = flask.session["user_id"]
    assert userid
    backend = sql_backend.get_db()
    csv_of = backend.run_basis(userid, int(tax_year))
    result = flask.send_file(
        csv_of, mimetype="text/csv", attachment_filename="basis.csv", as_attachment=True
    )
    return result


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


@yabc_api.route("/yabc/v1/users/<userid>", methods=["GET"])
def user_read(userid):
    backend = sql_backend.get_db()
    return backend.user_read(userid)


@yabc_api.route("/yabc/v1/users", methods=["POST"])
def user_create():
    name = flask.request.args.get("username")
    backend = sql_backend.get_db()
    return backend.user_create(name)
