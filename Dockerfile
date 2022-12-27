FROM python:bullseye

EXPOSE 8000
USER 0

# Install signal-cli
RUN curl -sL -o /etc/apt/trusted.gpg.d/morph027-signal-cli.asc https://packaging.gitlab.io/signal-cli/gpg.key &&\
	echo "deb https://packaging.gitlab.io/signal-cli signalcli main" | tee /etc/apt/sources.list.d/morph027-signal-cli.list &&\
	apt-get update &&\
	apt-get install -y \
	signal-cli-native signal-cli-dbus-service

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /app
WORKDIR /app
COPY . . 

CMD ["uvicorn", "signal_bot.backend.api.main:app", "--host=0.0.0.0", "--port=80"]