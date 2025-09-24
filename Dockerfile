FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


RUN chmod +x ./start.sh

EXPOSE 8080 8200

CMD [ "./start.sh" ]