FROM python:3-alpine3.10
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["python3", "bot.py"]