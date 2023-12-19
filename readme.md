# Objective

# Design considerations

This script can be run standalone, but it is design to be run with Airflow.
The implication of this is that it follows a fail fast approach.
Retry and error notification are delegated to Airflow, this makes the code less clutter.

The result is a CSV, that is generated manually. There is no 