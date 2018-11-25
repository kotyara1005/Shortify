# Shortify  [![Build Status](https://travis-ci.org/kotyara1005/Shortify.svg?branch=master)](https://travis-ci.org/kotyara1005/Shortify) [![codecov](https://codecov.io/gh/kotyara1005/Shortify/branch/master/graph/badge.svg)](https://codecov.io/gh/kotyara1005/Shortify) [![Requirements Status](https://requires.io/github/kotyara1005/Shortify/requirements.svg?branch=master)](https://requires.io/github/kotyara1005/Shortify/requirements/?branch=master)
Shortify is a bit.ly clone.
## Run app
```bash
docker-compose up
```
## Run tests
```bash
docker run --name some-redis -d redis -p 6666:6379
pytest --cov=./shortify/shortify.py --cov=./blacklist/blacklist.py .
```
