FROM python:3-slim

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY --chmod=777 . .

ENTRYPOINT ["python", "./KeyWhisperers.py", "test/JdP_001_input", "test/JdP_001_dictionary", "test/JdP_001_hash"]