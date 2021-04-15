import scrapy
import hashlib
from SI507Final.items import gameItem


class GameParameterSpider(scrapy.Spider):
    name = "games_params_spider"

    def __init__(self, platform, page=-1, **kwargs):
        super().__init__(**kwargs)
        self.page = page
        self.platform = platform
        self.url_ = f"https://www.metacritic.com/browse/games/score/metascore/all/{platform}/filtered?page={page}"

    def start_requests(self):
        yield scrapy.Request(url=self.url_, callback=self.parse)

    def parse(self, response, **kwargs):
        game_links = response.xpath(
            "//table[has-class('clamp-list')]/tr/td[has-class('clamp-summary-wrap')]/a[has-class('title')]/@href").getall()
        yield from response.follow_all(game_links, self.parse_game)

    def parse_game(self, response):
        # region basic information: name, summary, platform, publishers, release date
        name = response.xpath("//div[has-class('product_title')]/a/h1/text()").get()
        try:
            summary = response.xpath("//span[has-class('blurb_expanded')]/text()").get().strip()
        except AttributeError:
            summary = response.xpath("//span[has-class('data')]/span/text()").get().strip()
        try:
            platform = response.xpath("//span[has-class('platform')]/a/text()").get().strip()
        except AttributeError:
            platform = response.xpath("//span[has-class('platform')]/text()").get().strip()
        publishers = response.xpath("//li[has-class('publisher')]/span[has-class('data')]/a/text()").getall()
        releaseDate = response.xpath("//li[has-class('release_data')]/span[has-class('data')]/text()").getall()
        publishers = ", ".join([publisher.strip() for publisher in publishers])
        # endregion
        # region scores
        print("publishers:", publishers)
        metaScore = response.xpath("//div[has-class('metascore_summary')]/div/a/div/span/text()").get()
        userScore = response.xpath("//div[has-class('userscore_wrap')]/a/div/text()").get()
        print("metaScore:", metaScore)
        print("userScore:", userScore)
        meta_positiveScore = 0
        meta_mixedScore = 0
        meta_negativeScore = 0
        metaCritics = response.xpath(
            "//div[has-class('critic_reviews_module')]/div[has-class('body')]/div/div/ol/li/div")
        for metaCritic in metaCritics:
            if metaCritic.xpath("span[has-class('label')]/text()").get().startswith("Positive"):
                print("Positive")
                score = metaCritic.xpath("span[has-class('data')]/a/span/span[has-class('count')]/text()").get()
                if score is not None:
                    meta_positiveScore = int(score.replace(",", ""))
                else:
                    meta_positiveScore = 0
            elif metaCritic.xpath("span[has-class('label')]/text()").get().startswith("Mixed"):
                print("Mixed")
                score = metaCritic.xpath("span[has-class('data')]/a/span/span[has-class('count')]/text()").get()
                if score is not None:
                    meta_mixedScore = int(score.replace(",", ""))
                else:
                    meta_mixedScore = 0

            elif metaCritic.xpath("span[has-class('label')]/text()").get().startswith("Negative"):
                print("Negative")
                score = metaCritic.xpath("span[has-class('data')]/a/span/span[has-class('count')]/text()").get()
                if score is not None:
                    meta_negativeScore = int(score.replace(",", ""))
                else:
                    meta_negativeScore = 0

        user_positiveScore = 0
        user_mixedScore = 0
        user_negativeScore = 0
        metaCritics = response.xpath("//div[has-class('user_reviews_module')]/div[has-class('body')]/div/div/ol/li/div")
        for metaCritic in metaCritics:
            if metaCritic.xpath("span[has-class('label')]/text()").get().startswith("Positive"):
                print("Positive")
                score = metaCritic.xpath("span[has-class('data')]/a/span/span[has-class('count')]/text()").get()
                if score is not None:
                    user_positiveScore = int(score.replace(",", ""))
                else:
                    user_positiveScore = 0
            elif metaCritic.xpath("span[has-class('label')]/text()").get().startswith("Mixed"):
                print("Mixed")
                score = metaCritic.xpath("span[has-class('data')]/a/span/span[has-class('count')]/text()").get()
                if score is not None:
                    user_mixedScore = int(score.replace(",", ""))
                else:
                    user_mixedScore = 0

            elif metaCritic.xpath("span[has-class('label')]/text()").get().startswith("Negative"):
                print("Negative")
                score = metaCritic.xpath("span[has-class('data')]/a/span/span[has-class('count')]/text()").get()
                if score is not None:
                    user_negativeScore = int(score.replace(",", ""))
                else:
                    user_negativeScore = 0
        # endregion

        game = gameItem.Game(id=id,
                             name=name,
                             summary=summary,
                             platform=platform,
                             releaseDate=releaseDate,
                             publisher=publishers,
                             userScore=userScore,
                             metaScore=metaScore,
                             user_positive=user_positiveScore,
                             user_mixed=user_mixedScore,
                             user_negative=user_negativeScore,
                             meta_positive=meta_positiveScore,
                             meta_mixed=meta_mixedScore,
                             meta_negative=meta_negativeScore
                             )

        return game

