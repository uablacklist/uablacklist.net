FROM python:3-alpine

WORKDIR /usr/src/app

RUN apk update && apk add bind-tools whois

RUN pip install Jinja2 pytz

COPY scripts/ .

CMD ["python", "-u", "generator.py", "/out"]