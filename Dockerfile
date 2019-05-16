FROM python:3.6.2

COPY ./app /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT [ "python" ]

CMD [ "whoami.py" ]
