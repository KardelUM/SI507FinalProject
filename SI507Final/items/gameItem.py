import scrapy
class Game(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    summary = scrapy.Field()
    platform = scrapy.Field()
    releaseDate = scrapy.Field()
    publisher = scrapy.Field()
    img_url = scrapy.Field()
    userScore = scrapy.Field()
    metaScore = scrapy.Field()
    user_positive = scrapy.Field()
    user_mixed = scrapy.Field()
    user_negative = scrapy.Field()
    meta_positive = scrapy.Field()
    meta_mixed = scrapy.Field()
    meta_negative = scrapy.Field()

