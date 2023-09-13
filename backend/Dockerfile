FROM python:3.10-slim

RUN apt-get update && apt-get -y install tesseract-ocr

RUN pip install pipenv

ENV SRC_DIR /usr/local/src/timetable_scanner

WORKDIR ${SRC_DIR}

COPY Pipfile Pipfile.lock ${SRC_DIR}/

RUN pipenv install --system --clear

COPY ./ ${SRC_DIR}/

WORKDIR ${SRC_DIR}/flask_app

CMD ["python", "calendarScanner2.py"]