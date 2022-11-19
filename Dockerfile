FROM python:3.9.4
COPY .  /squawker_web
WORKDIR /squawker_web
RUN pip install -r requirements.txt
EXPOSE  8000
CMD ["python", "wsgi.py"]