# README

## Introduction

This project is a Flask& MySQL-based project to represents controversial games on [Metacritic](https://www.metacritic.com/).

It is the final project for SI507.



## Installation

The dependency for this project is 

mysql-connector-python

scrapy

scrapyrt 

flask

flask-restful

hashlib

json

wordcloud

## Execution

There are three ways to run this project

### Retrieve Everything by Scrapy

```
scrapy crawl all_games -a start_page=1 -a end_page=30
<Wait for much times...>
cd flaskProject
flask run
```

###  Retrieve All Information from .sqldump

There is a sqldump file in the root directory.

### Run "Temporary Server"

```
scrapyrt
<open another terminal>
cd flaskProject
flask run
<browse the 127.0.0.1:5000/index2>
```

