# For more information, please refer to https://aka.ms/vscode-docker-python
FROM regaptdb.azurecr.io/aptdb-base:1.0

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# changing user
RUN adduser --system pyuser
RUN usermod -aG sudo pyuser
USER root

# updating pip
# RUN python -m pip install --upgrade pip

# Changing to root
USER root

RUN apt-get update
#  && apt-get -y install tesseract-ocr \
#  && apt-get -y install ffmpeg libsm6 libxext6

# cd to user directory
WORKDIR /home/pyuser

# Create app directory
# RUN mkdir aptdb

COPY . aptdb/
RUN chown -R pyuser aptdb

# changing user
# USER pyuser

# Changing working dir
WORKDIR /home/pyuser/aptdb

#RUN mkdir /home/pyuser/aptdb/src
#RUN mkdir /home/pyuser/aptdb/logs
#RUN mkdir /home/pyuser/aptdb/data

# Install pip requirements
# RUN pip install -r requirements.txt
CMD ["python", "main.py"]
EXPOSE 8080
