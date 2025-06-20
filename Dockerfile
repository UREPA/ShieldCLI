FROM python:3.13-slim

WORKDIR /app

COPY ./shieldcli ./shieldcli
COPY requirements.txt ./
COPY reports.db ./

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "shieldcli.api:app", "--host", "0.0.0.0", "--port", "8000"]

#docker build -t shieldcli-api .
#docker run -p 8000:8000 shieldcli-api