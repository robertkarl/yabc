build: src
	docker build --tag yabc .

run:
	rm -f tmp.db
	PYTHONPATH=src python -m yabc.server.server

run_docker:
	docker run -it --publish 127.0.0.1:5000:5000 yabc

test_local:
	curl --data-binary @testdata/synthetic_coinbase_csv.csv -X POST localhost:5000/yabc/v1/taxdocs?exchange=coinbase&userid=1
	curl --data-binary @testdata/synthetic_gemini_csv.csv -X POST localhost:5000/yabc/v1/taxdocs?exchange=gemini&userid=1
	curl -X POST localhost:5000/yabc/v1/run_basis?userid=1

test_buyone_sellone:
	curl -X POST localhost:5000/yabc/v1/add_user/testuser
	curl --data-binary @testdata/synthetic_buyone_sellone_coinbase.csv -X POST localhost:5000/yabc/v1/add_document/coinbase/testuser
	curl -X POST localhost:5000/yabc/v1/run_basis/testuser

test_adhoc:
	curl -X POST localhost:5000/yabc/v1/add_user/newuser
	curl -X POST --data '{"Transfer Total": "1234", "Transfer Fee": "12", "Amount": "1", "Timestamp": "5/6/07 1:12"}' localhost:5000/yabc/v1/add_tx/newuser
	curl -X POST --data '{"Transfer Total": "1299", "Transfer Fee": "12", "Amount": "-1", "Timestamp": "5/6/07 1:12"}' localhost:5000/yabc/v1/add_tx/newuser
	curl -X POST localhost:5000/yabc/v1/run_basis/newuser

test_all: test_adhoc test_local test_buyone_sellone

.PHONY: build test_all test_adhoc test_local test_buyone_sellone
