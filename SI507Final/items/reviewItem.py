import scrapy


class Review(scrapy.Item):
    """
    This is a Item class about reviews
    type: the type of the review. It has 2 values: "meta" and "user"
    score: int value, the remark score of the review
    date: the review date
    content: The text part of the review
    source: The reviewer
    game_id: foreigner key. It related to the game of review.
    """
    type = scrapy.Field()
    score = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()
    game_id = scrapy.Field()