FROM python:3.8

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    unixodbc-dev \
    curl \
    apt-transport-https \
    gnupg2

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

ENV TZ=America/Bogota
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY data_builder_sir.py .
COPY data_builder_sales.py .
COPY main.py .
COPY maxpoint_credentials.py .
COPY get_data_recetas.sql .
COPY get_data_sales.sql .

CMD [ "python", "main.py" ]