build: src
	docker build --tag yabc .

run:
	docker run -it --publish 127.0.0.1:5000:5000 yabc

test_local:
	curl --data-binary @testdata/synthetic_coinbase_csv.csv -X POST localhost:5000/add_document/coinbase/rk
	curl --data-binary @testdata/synthetic_gemini_csv.csv -X POST localhost:5000/add_document/gemini/rk
	curl -X POST localhost:5000/run_basis/rk

test_buyone_sellone:
	curl --data-binary @testdata/synthetic_buyone_sellone_coinbase.csv -X POST localhost:5000/add_document/coinbase/testuser
	curl -X POST localhost:5000/run_basis/testuser

test_adhoc:
	curl -X POST --data '{"Transfer Total": "1234", "Transfer Fee": "12", "Amount": "1", "Timestamp": "5/6/07 1:12"}' localhost:5000/add_tx/newuser
	curl -X POST --data '{"Transfer Total": "1299", "Transfer Fee": "12", "Amount": "-1", "Timestamp": "5/6/07 1:12"}' localhost:5000/add_tx/newuser
	curl -X POST localhost:5000/run_basis/newuser

.PHONY: build
