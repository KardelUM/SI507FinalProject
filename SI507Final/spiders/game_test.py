import hashlib

import scrapy

from SI507Final.items import gameItem
from SI507Final.items import reviewItem


class GameParameterSpider(scrapy.Spider):
    name = "game_test"
    start_urls = ["https://www.metacritic.com/game/playstation-4/the-last-of-us-part-ii"]

    def __init__(self, name=None, **kwargs):
        super().__init__(name)

    def parse(self, response, **kwargs):
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
        releaseDate = response.xpath("//li[has-class('release_data')]/span[has-class('data')]/text()").get()
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
        print("meta positive", meta_positiveScore)
        print("meta mixed", meta_mixedScore)
        print("meta negative", meta_negativeScore)
        print("user positive", user_positiveScore)
        print("user mixed", user_mixedScore)
        print("user negative", user_negativeScore)
        # endregion

        # use basic information of a game as id
        id = hashlib.sha256((name + platform + summary + releaseDate + publishers).encode("utf-8")).hexdigest()

        # region
        user_review_link = response.xpath("//div[has-class('metascore_summary')]/div/a/@href").get()
        meta_review_link = response.xpath("//div[has-class('userscore_wrap')]/a/@href").get()
        yield response.follow(user_review_link, self.parse_user_review, meta={"id": id})
        yield response.follow(meta_review_link, self.parse_meta_review, meta={"id": id})
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

    def parse_meta_review(self, response):
        game_id = response.meta.get("id")
        all_review_sections = response.xpath("//div[has-class('review_section')]")
        for review_section in all_review_sections:
            source = review_section.xpath("div[has-class('review_stats')]/div[has-class('review_critic')]/div[has-class('source')]/text()").get()
            date = review_section.xpath("div[has-class('review_stats')]/div[has-class('review_critic')]/div[has-class('date')]/text()").get()
            score = review_section.xpath("div[has-class('review_stats')]/div[has-class('review_grade')]/div/text()").get()
            content = review_section.xpath("/div[has-class('review_body')]/text()").get()
            print("source:", source, file="log.txt")
            print("date:", date, file="log.txt")
            print("score:", score, file="log.txt")
            print("content:", content, file="log.txt")

            score = int(score)
            yield reviewItem.Review(type="meta",
                                    score=score,
                                    date=date,
                                    content=content,
                                    source=source,
                                    game_id=game_id)

    def parse_user_review(self, response):
        game_id = response.meta.get("id")
        all_review_sections = response.xpath("//div[has-class('review_section')]")
        for review_section in all_review_sections:
            source = review_section.xpath(
                "/div[has-class('review_stats')]/div[has-class('review_critic')/div[has-class('name')]]/text()").get()
            date = review_section.xpath(
                "/div[has-class('review_stats')]/div[has-class('review_critic')/div[has-class('date')]]/text()").get()
            score = review_section.xpath(
                "/div[has-class('review_stats')]/div[has-class('review_grade')/div/text()").get()
            score = int(score)
            # consider expanded
            content = review_section.xpath("/div[has-class('review_body')]/text()").get()

            yield reviewItem.Review(type="user",
                                    score=score,
                                    date=date,
                                    content=content,
                                    source=source,
                                    game_id=game_id)