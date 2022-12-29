FROM python:bullseye

USER 0

# Install signal-cli
RUN curl -sL -o /etc/apt/trusted.gpg.d/morph027-signal-cli.asc https://packaging.gitlab.io/signal-cli/gpg.key && \
	echo "deb https://packaging.gitlab.io/signal-cli signalcli main" | tee /etc/apt/sources.list.d/morph027-signal-cli.list && \
	apt-get update && \
	apt-get install -y \
	signal-cli-native signal-cli-dbus-service


# Install python requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


# Copy app files
RUN mkdir /app
WORKDIR /app
COPY . .

# Create data directory to asses rights
RUN mkdir /data


# Create user and chown /app /data
RUN groupadd -g 10001 signal-bot && \
	useradd --no-log-init -u 10000 -g signal-bot signal-bot && \
	chown -R signal-bot:signal-bot /app /data

USER signal-bot:signal-bot


CMD ["uvicorn", "signal_bot.backend.api.main:app", "--host=0.0.0.0", "--port=80"]