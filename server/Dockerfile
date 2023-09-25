FROM python:3.10-slim

RUN apt-get update && apt-get -y install tesseract-ocr

RUN pip install pipenv

ENV SRC_DIR /usr/local/src/timetable_scanner

WORKDIR ${SRC_DIR}

COPY Pipfile Pipfile.lock ${SRC_DIR}/

RUN pipenv install --system --clear

COPY ./ ${SRC_DIR}/

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--log-level=debug", "app:app"]
#CMD ["python", "app.py"]