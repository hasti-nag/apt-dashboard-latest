# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# changing user
RUN adduser --system pyuser
RUN usermod -aG sudo pyuser
USER root

# updating pip
RUN python -m pip install --upgrade pip

# Changing to root
USER root

RUN apt-get update

# cd to user directory
WORKDIR /home/pyuser

# Create app directory
RUN mkdir aptdb

COPY requirements.txt aptdb/
RUN chown -R pyuser aptdb

# changing user
# USER pyuser

# Changing working dir
WORKDIR /home/pyuser/aptdb

RUN mkdir /home/pyuser/aptdb/src
RUN mkdir /home/pyuser/aptdb/logs
RUN mkdir /home/pyuser/aptdb/data

# Install pip requirements
RUN pip install -r requirements.txt

