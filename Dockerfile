FROM python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8080
COPY . .
CMD ["python", "app.py"]
