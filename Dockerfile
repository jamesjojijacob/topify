FROM python:3.6.8-jessie
RUN apt-get update && apt-get install -y \
    libev4 \
    libev-dev \
    build-essential \
    python-dev
WORKDIR /myapp
COPY . /myapp
RUN pip install -U -r requirements.txt
RUN cd /myapp/libraries && python -u /myapp/libraries/setup.py install
EXPOSE 8080
CMD ["python", "app.py"]