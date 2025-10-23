FROM localhost/fft:fft_dependencies AS compile-image

FROM python:3.9.16 AS build-image

COPY --from=compile-image /usr/local/share/ca-certificates/ /usr/local/share/ca-certificates/
COPY --from=compile-image /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=compile-image /opt/venv /opt/venv

RUN update-ca-certificates

ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

ENV PATH="/opt/venv/bin:$PATH"

# 1. Install OS packages
RUN echo "Acquire { http::User-Agent \"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0\";};" > /etc/apt/apt.conf

RUN apt-get update && apt-get -y install cron vim unixodbc-dev gnupg2 gpg curl

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/18.04/prod bionic main" | tee /etc/apt/sources.list.d/mssql-release.list
RUN export ACCEPT_EULA='y' && DEBIAN_FRONTEND=noninteractive apt-get update && apt-get -y install msodbcsql18 mssql-tools18
RUN export  DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get -y install dnsutils git krb5-user

# 2. Set working directory for FFT project in container
WORKDIR /app

# 3. Add variables to PATH variable
ADD krb5.conf .
RUN echo 'PATH="/opt/mssql-tools18/bin:$PATH"' >> .profile

# 4. Configure SSL to acknowldge the firewall policy for RL6 database to be accessed by staging environment
RUN sed -i "s|MinProtocol = TLSv1.2|MinProtocol = TLSv1.0 |g" /etc/ssl/openssl.cnf
RUN sed -i "s|CipherString = DEFAULT@SECLEVEL=2|CipherString = DEFAULT@SECLEVEL=1 |g" /etc/ssl/openssl.cnf

# 5. Copy relevant files into the app project folder
COPY config.yaml main.py .
COPY scripts/ /app/scripts/
COPY tests/ /app/tests/
COPY data/ /app/data/


RUN ls

# 6. Schedule main.py to run at midnight of everyday
COPY crontab /etc/cron.d/crontab

RUN chmod 0644 /etc/cron.d/crontab && \
   /usr/bin/crontab /etc/cron.d/crontab && \
   touch /tmp/out.log

CMD cron && tail -f /tmp/out.log
