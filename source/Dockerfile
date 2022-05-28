FROM python:3.10-slim

# Change the working directory to the root of the project
WORKDIR /srv/flask_app

# Install dependencies
RUN apt update -y && apt install -y xvfb curl wget bzip2 libasound2 libc-bin libxtst6 packagekit-gtk3-module libx11-xcb-dev libdbus-glib-1-2 libxt6 libpci-dev && rm -rf /var/lib/apt/lists/*

# Install geckodriver
RUN GECKODRIVER_VERSION=`curl -L -s -H 'Accept: application/json' https://github.com/mozilla/geckodriver/releases/latest | sed -e 's/.*"tag_name":"\([^"]*\)".*/\1/'` && \
wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
chmod +x /usr/local/bin/geckodriver && \
rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

# Install firefox web browser
RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP

# Install the dependencies
COPY requirements.txt /srv/flask_app/
RUN pip install -r requirements.txt --src /usr/local/src --no-warn-script-location

# Copy the source code to the working directory
COPY source /srv/flask_app
RUN chmod +x run.sh

# Run the app
CMD ./run.sh