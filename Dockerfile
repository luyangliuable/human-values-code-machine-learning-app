# pull official base image
FROM python:3.9.1-slim-buster

# set work directory
WORKDIR /usr/src/app

# Install git
RUN apt update
RUN apt install git -y

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

RUN echo env
