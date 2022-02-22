#  Custom spider

Web crawler to online store: https://gplay.bg/

We take the following data of an item:
category, subcategory, title, subtitle, number of the product, price

The scraped data is stored in a sqlite3 database.

## Installation

pip install - r requirements.txt

## Usage 

From the project directory "gplay_scraper" to run a spider scrapy crawl categories.
database.py file create database. It is executed by opening it and starting with a run.
The file wtih database (gplay_store.db) should be located in the directory of the scrapy.cfg file. 
When open https://sqliteonline.com/ and open the file: gplay_store.bg
we can see the database and execute queries with it to check whether the terms of the job are met.



