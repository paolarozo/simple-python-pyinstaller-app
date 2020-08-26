FROM python:3-alpine

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN rm requirements.txt

CMD python