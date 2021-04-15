import scrapy


class Review(scrapy.Item):
    type = scrapy.Field()
    score = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()
    game_id = scrapy.Field()