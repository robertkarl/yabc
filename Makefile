URL=localhost:5000/yabc/v1

build: src
	docker build --tag yabc .

run:
	PYTHONPATH=src FLASK_APP=wwwd FLASK_ENV=development flask run

run_docker:
	docker run -it --publish 127.0.0.1:5000:5000 yabc

create_test_user:
	curl -X POST ${URL}/users?username=robert

test_local: 
	curl --data-binary @testdata/synthetic_coinbase_csv.csv "${URL}/taxdocs?exchange=coinbase&userid=1"
	curl --data-binary @testdata/synthetic_gemini_csv.csv "${URL}/taxdocs?exchange=gemini&userid=1"
	curl -X POST localhost:5000/yabc/v1/run_basis?userid=1 2>/dev/null | grep 15027

test_buyone_sellone:
	curl -X POST ${URL}/users?username=testuser
	curl --data-binary @testdata/synthetic_buyone_sellone_coinbase.csv \
			"${URL}/taxdocs?exchange=coinbase&userid=2"
	curl -X POST localhost:5000/yabc/v1/run_basis?userid=2

test_adhoc:
	curl -X POST ${URL}/users?username=testuser
	curl --data '{"Transfer Total": "1234", "Transfer Fee": "12", "Amount": "1", "Timestamp": "5/6/07 1:12"}' ${URL}/transactions?userid=3
	curl --data '{"Transfer Total": "1299", "Transfer Fee": "12", "Amount": "-1", "Timestamp": "5/6/07 1:12"}' "${URL}/transactions?userid=3"
	curl -X POST "${URL}/run_basis?userid=3" 2>/dev/null | grep 41

test_all:
	make create_test_user
	make test_local
	make test_buyone_sellone
	make test_adhoc

.PHONY: build test_all test_adhoc test_local test_buyone_sellone
