import mysql.connector
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from SI507Final.items import gameItem, reviewItem


class Si507FinalPipeline:
    conf = {
        'host': '127.0.0.1',
        'user': 'kardel',
        'password': 'alksdj1029a',
        'database': 'SI507',
        'raise_on_warnings': True
    }
    def __init__(self):
        self.conn = mysql.connector.connect(user="kardel", password="alksdj1029a", host="localhost", database="SI507")
    def open_spider(self, spider):
        print("spider open!")
    def process_item(self, item, spider):
        self.save(item)
        return item
    def close_spider(self, spider):
        self.conn.close()
    def save(self, item):
        cursor = self.conn.cursor()
        if type(item) == gameItem.Game:
            create_query = "INSERT INTO Game (id, name, content, platform, releaseDate, publisher, userScore, metaScore, user_positive, user_mixed, user_negative, meta_positive, meta_mixed, meta_negative) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            row = (item['id'], item['name'], item['summary'], item['platform'], item['releaseDate'], item['publisher'], item['userScore'], item['metaScore'], item['user_positive'], item['user_mixed'], item['user_negative'], item['meta_positive'], item['meta_mixed'], item['meta_negative'])
        elif type(item) == reviewItem.Review:
            create_query = "INSERT INTO review (type, score, date, content, source, game_id) VALUES (%s, %s, %s, %s, %s, %s)"
            row = (item['type'], item['score'], item['date'], item['content'], item['source'], item['game_id'])
        cursor.execute(create_query, row)
        self.conn.commit()
        cursor.close()


class SelectiveSpiderPipelines:
    def __init__(self):
        pass
    def open_spider(self, spider):
        print("spider open!")
    def process_item(self, item, spider):
        return item