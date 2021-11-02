FROM python:3

# set env variables
ENV PYTHONUNBUFFERED 1

WORKDIR /code
# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .

COPY . .

ENTRYPOINT ["/code/entrypoint.sh"]