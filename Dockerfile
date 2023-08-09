# syntax=docker/dockerfile:1
FROM python:3.9.13

WORKDIR /SasWebCalc

# Bundle app source
COPY . /SasWebCalc

# Intall Webcalc
RUN python3 -m pip install pip --upgrade

# Move the documentation to the correct location
COPY docs/build/html webcalc/templates/docs
RUN python3 -m pip install /SasWebCalc/

ENV PYTHONPATH "/SasWebCalc/"
COPY gunicorn_configuration.py /etc/

EXPOSE 5000/tcp

ENTRYPOINT ["gunicorn"]

WORKDIR /SasWebCalc/webcalc

CMD ["-b 0.0.0.0:5000", "--config=/../etc/gunicorn_configuration.py", "wsgi:application"]
