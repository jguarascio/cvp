# Redrop

A quick script in python 2 that will move files from one folder to another. Intended to run as a cron job. Handles the situation where a file falls to a DLQ due to network issues or timeout and a simple redrop is all that is needed. Uses a configurable threshold so that it will not try to redrop files in the event of a network outage.