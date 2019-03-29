FROM ubuntu

####
# Python environment setup
RUN apt update
RUN apt upgrade -y 2>/dev/null # 3-20-2019
RUN apt install python3 python3-pip -y
RUN pip3 install --upgrade pip
RUN  pip3 install --upgrade setuptools

####
# Application dependencies and setup

RUN pip3 install flask
RUN pip3 install python-dateutil

ENV FLASK_DEBUG=true
ENV YABC_DEBUG=true
EXPOSE 5000

WORKDIR /yabc
ADD . /yabc
RUN python3 ./setup.py install 

ENTRYPOINT python3 -m yabc.server.yabc_api
