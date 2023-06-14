# syntax=docker/dockerfile:1
FROM python:3.9.13

WORKDIR /SasWebCalc

# Intall Webcalc
RUN python3 -m pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org --upgrade pip -r requirements.txt


# Bundle app source
COPY . .

# Move the documentation to the correct location
COPY docs webcalc/templates/docs
RUN python3 -m pip install /SasWebCalc/

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
