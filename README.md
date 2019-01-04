# JiKePan

JiKePan is a mobile-ready web file sharing system for course teaching.

### Tech

JiKePan uses a number of open source projects to work properly:

* Flask
* Bootstrap
* Sqlite
* jQuery

### Installation

JiKePan requires Pipenv and Python 3.6 or above to run.

Install the dependencies and dev-dependencies from Pipfile using Pipenv, initialize the database and start the server.

```sh
$ pipenv install
$ pipenv run python database.py
$ pipenv run python view.py
```
