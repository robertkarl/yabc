FROM ubuntu

####
# Python environment setup
RUN apt update 2>/dev/null # 5-9-2019
RUN apt upgrade -y 2>/dev/null # 5-9-2019
RUN apt install python3 python3-pip -y 2>/dev/null
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools


####
# Application dependencies and setup
EXPOSE 5000
RUN pip3 install flask 2>/dev/null
RUN pip3 install python-dateutil 2>/dev/null

WORKDIR /yabc
ADD . /yabc
RUN python3 ./setup.py install  2>/dev/null

# Required by click, a flask dep
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENV FLASK_ENV=development
ENV FLASK_APP=yabc.app

ENTRYPOINT flask init-db && flask run --host='0.0.0.0'
