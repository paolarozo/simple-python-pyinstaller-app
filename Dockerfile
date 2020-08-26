FROM python:3-alpine

RUN bash -c "pip uninstall -y -r <(pip freeze)"
RUN pip install --upgrade pip
RUN pip install coverage

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN rm requirements.txt

CMD python