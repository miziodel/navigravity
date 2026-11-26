FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src/ /app/

CMD ["python", "-m", "navidrome_mcp_server"]