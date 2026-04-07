FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install flask
RUN pip install requests
CMD ["python", "-u", "catalog.py"]
