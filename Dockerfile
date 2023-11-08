FROM python:3.8-slim
RUN apt-get update && apt-get install -y --no-install-recommends cron tzdata lsb-release build-essential curl gnupg
RUN apt-get update && apt-get install -y --no-install-recommends python3-dev python3-virtualenv
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && apt-get install -y --no-install-recommends tdsodbc unixodbc-dev
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends mssql-tools msodbcsql17
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
WORKDIR /usr/src/reports_data_import
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m pip install virtualenv
RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY . ./
RUN pip install -r requirements.txt
RUN mv ./crontab /etc/cron.d/cron-jobs && sed -i -e 's/\r/\n/g' /etc/cron.d/cron-jobs && chmod 0644 /etc/cron.d/cron-jobs
RUN chmod +x cron.sh
RUN mkdir -p /var/log/cron && touch /var/log/cron/cron.log
ENV TZ="Asia/Shanghai"
ENTRYPOINT ["/bin/sh", "/usr/src/reports_data_import/cron.sh"]