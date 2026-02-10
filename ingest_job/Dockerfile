FROM python:3.12-alpine

WORKDIR /app

COPY . .

RUN pip install uv && uv sync

CMD ["uv", "run", "python", "src/main.py"]
