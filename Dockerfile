FROM python:3.9-slim

WORKDIR /coursevault

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run.py"] 