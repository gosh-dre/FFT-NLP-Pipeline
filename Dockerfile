FROM python:3.8.16

# 1. Install OS packages
RUN echo "Acquire { http::User-Agent \"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0\";};" > /etc/apt/apt.conf

RUN apt-get update && apt-get -y install cron vim

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/18.04/prod bionic main" | tee /etc/apt/sources.list.d/mssql-release.list
RUN apt update
RUN ACCEPT_EULA=Y DEBIAN_FRONTEND=noninteractive apt-get -y install dnsutils git krb5-user msodbcsql18 mssql-tools18

# 2. Install Poetry
ENV PIP_DISABLE_PIP_VERSION_CHECK=on

RUN pip install poetry

# 2.1. Set working directory for FFT project in container
WORKDIR /app

COPY poetry.lock pyproject.toml config.yaml main.py /app/

RUN poetry config virtualenvs.create false &&\
    poetry lock --no-update &&\
    poetry install --no-interaction &&\
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu &&\
    pip install transformers

# 3. Add variables to PATH variable
ADD krb5.conf .
RUN echo 'PATH="/opt/mssql-tools18/bin:$PATH"' >> .profile

# 4. Configure SSL to acknowldge the firewall policy for RL6 database to be accessed by staging environment
RUN sed -i "s|MinProtocol = TLSv1.2|MinProtocol = TLSv1.0 |g" /etc/ssl/openssl.cnf
RUN sed -i "s|CipherString = DEFAULT@SECLEVEL=2|CipherString = DEFAULT@SECLEVEL=1 |g" /etc/ssl/openssl.cnf

# 5. Copy relevant files into the app project folder
#COPY main.py autoredactor.py datastorage.py modeller.py splitter.py ./app/scripts
#COPY feature_sentiment.pkl feature_theme.pkl sentiment-classifier.pkl tfidftransformer_sentiment.pkl tfidftransformer_theme.pkl theme-classifier.pkl ./models

COPY models/ ./models/
COPY scripts/ ./scripts/
COPY tests/ ./tests/
COPY data/ ./data/

# 6. Schedule main.py to run at midnight of everyday
COPY crontab /etc/cron.d/crontab

RUN chmod 0644 /etc/cron.d/crontab && \
   /usr/bin/crontab /etc/cron.d/crontab && \
   touch /tmp/out.log

CMD cron && tail -f /tmp/out.log
