FROM python:3.9.4
COPY .  /squawker_web
WORKDIR /squawker_web
RUN apt-get update -y && \
    apt-get install -y sudo make gcc
RUN pip install -r requirements.txt
RUN pytest > testresults.txt
EXPOSE  8000
CMD ["python", "wsgi.py"]
