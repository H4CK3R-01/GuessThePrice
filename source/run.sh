#!/bin/bash

# Start the first process
python bot.py &

# Start the second process
python daily_challenge.py &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
