FROM python:3.5.2

WORKDIR /usr/src/app

RUN pip install --upgrade pip
COPY . .
RUN pip install --no-cache-dir -r requirements-lint.txt
RUN pip install --no-cache-dir -r requirements-test.txt
RUN pip install --no-cache-dir -e .[tests]

COPY . .

CMD [ "pytest" ]