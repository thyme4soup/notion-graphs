FROM python:3.10
EXPOSE 8080
WORKDIR /src

# Install requirements
RUN apt-get update && apt-get -y install
RUN apt-get install -y graphviz graphviz-dev cmake
COPY ./requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy app files
ADD ./templates ./templates
COPY grapher.py .
COPY web_server.py .
COPY notion_helper.py .

ENV PYTHONUNBUFFERED=1
# CMD ["gunicorn", "--bind", "0.0.0.0:8080", "web_server:app"]
# gunicorn doesn't like it when i spin off processes in the app (rude)
CMD ["python", "web_server.py"]
