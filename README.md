# Compute Module

This module contains the scripts necessary to collect, process, and train upon rated songs.

Run npm install to install the necessary JS packages.

## npm run crunch
Fetches unprocessed videos from the database, processes them, and updates the videos on the DB

## npm run zip
Collects the data from processed videos in the DB, attaches labels from user entries, and outputs all data to a csv.

## npm run train
Runs the python script to train a linear regression model on the data and outputs metrics.
