URL=localhost:5000/yabc/v1

build: src
	docker build --tag yabc .

run:
	rm -f src/instance/*
	PYTHONPATH=src FLASK_APP=yabc.app FLASK_ENV=development flask init-db
	PYTHONPATH=src FLASK_APP=yabc.app FLASK_ENV=development flask run

run_no_devel:
	rm -f src/instance/*
	PYTHONPATH=src FLASK_APP=yabc.app flask init-db
	PYTHONPATH=src FLASK_APP=yabc.app flask run

run_docker:
	docker run -it --publish 127.0.0.1:5000:5000 yabc

create_test_user:
	curl -X POST ${URL}/users?username=testuser1

test_local: 
	curl -F taxdoc=@testdata/synthetic_coinbase_csv.csv "${URL}/taxdocs?exchange=coinbase&userid=1"
	curl -F taxdoc=@testdata/synthetic_gemini_csv.csv "${URL}/taxdocs?exchange=gemini&userid=1"
	curl -X POST localhost:5000/yabc/v1/run_basis?userid=1 | grep success
	curl -X POST localhost:5000/yabc/v1/download_8949/2008?userid=1 2>/dev/null | grep 15026

test_buyone_sellone:
	curl -X POST ${URL}/users?username=testuser2
	curl -F taxdoc=@testdata/synthetic_buyone_sellone_coinbase.csv \
			"${URL}/taxdocs?exchange=coinbase&userid=2"
	curl -X POST localhost:5000/yabc/v1/run_basis?userid=2

test_adhoc:
	curl -X POST ${URL}/users?username=testuser3
	curl --data tx='{"Currency": "BTC", "Transfer Total": "1234", "Transfer Fee": "12", "Amount": "1", "Timestamp": "5/6/07 1:12"}' ${URL}/transactions?userid=3
	curl --data tx='{"Transfer Total": "1299", "Currency": "BTC", "Transfer Fee": "12", "Amount": "-1", "Timestamp": "5/6/07 1:12"}' "${URL}/transactions?userid=3"
	curl -X POST "${URL}/run_basis?userid=3" | grep success
	curl -X POST "${URL}/download_8949/2007?userid=3" 2>/dev/null | grep 'total,41'

test_all:
	make create_test_user
	make test_local
	make test_buyone_sellone
	make test_adhoc

pypi_deploy:
	rm -f dist/*
	python3 setup.py sdist bdist_wheel
	TWINE_USERNAME=robertkarl python3 -m twine upload dist/* --skip-existing


.PHONY: build test_all test_adhoc test_local test_buyone_sellone pypi_deploy
