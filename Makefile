URL=localhost:5000/yabc/v1

build: src
	docker build --tag yabc .

nuke_db_and_run:
	./nuke_db_and_run

run:
	PYTHONPATH=src FLASK_APP=yabc.app FLASK_ENV=development flask run

run_no_devel:
	PYTHONPATH=src FLASK_APP=yabc.app flask run

run_docker:
	docker run -it --publish 127.0.0.1:5000:5000 yabc

create_test_users:
	curl -X POST ${URL}/users?username=testuser1
	curl -X POST ${URL}/users?username=testuser2
	curl -X POST ${URL}/users?username=testuser3

test_coinbase_gemini_totals:
	PYTHONPATH=src python -m yabc testdata/gemini/sample_gemini.xlsx testdata/coinbase/sample_coinbase.csv  | grep 'total gain.*21090'

test_buyone_sellone:
	curl -F taxdoc=@testdata/coinbase/buyone_sellone.csv "${URL}/taxdocs?exchange=coinbase&user_id=2"
	curl -X POST localhost:5000/yabc/v1/run_basis?user_id=2

test_adhoc:
	curl --data tx='{"Currency": "BTC", "Transfer Total": "1234", "Transfer Fee": "12", "Amount": "1", "Timestamp": "5/6/07 1:12"}' ${URL}/transactions?user_id=3
	curl --data tx='{"Transfer Total": "1299", "Currency": "BTC", "Transfer Fee": "12", "Amount": "-1", "Timestamp": "5/6/07 1:12"}' "${URL}/transactions?user_id=3"
	curl -X POST "${URL}/run_basis?user_id=3" | grep success
	curl "${URL}/download_8949/2007?user_id=3" 2>/dev/null | grep 'total,41'

test_all:
	make create_test_users
	make test_local
	make test_buyone_sellone
	make test_adhoc
	echo -e '\nTests succeeded!'

pypi_deploy:
	rm -f dist/*
	python3 setup.py sdist bdist_wheel
	TWINE_USERNAME=robertkarl python3 -m twine upload dist/* --skip-existing


.PHONY: build test_all test_coinbase_gemini_totals test_adhoc test_local test_buyone_sellone pypi_deploy nuke_db_and_run
