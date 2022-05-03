FROM python:3.10-slim

# Change the working directory to the root of the project
WORKDIR /srv/flask_app

# Install the dependencies
COPY requirements.txt /srv/flask_app/
RUN pip install -r requirements.txt --src /usr/local/src --no-warn-script-location

# Copy the source code to the working directory
COPY source /srv/flask_app

# Run the app
CMD ["python", "bot.py"]