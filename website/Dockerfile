FROM python:3.10.0-alpine
RUN mkdir -p /website
COPY . /website
WORKDIR /website
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
ENV FLASK_APP=main.py
CMD ["flask", "run", "--host", "0.0.0.0"]
