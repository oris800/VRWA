FROM python:3.9-slim

RUN apt-get update && apt-get install -y iputils-ping bash
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x ./start.sh

EXPOSE 8080 8200

CMD ["./start.sh"]