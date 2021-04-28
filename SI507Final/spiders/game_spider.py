import hashlib
import os
import pickle

import mysql.connector

import scrapy

from SI507Final.items import gameItem, reviewItem


class AllGameSpider(scrapy.Spider):
    name = "all_games"

    def __init__(self, start_page=1, end_page=12, **kwargs):
        super().__init__(**kwargs)
        self.urls = []
        start_page = int(start_page)
        end_page = int(end_page)
        # [start_page, end_page]
        for i in range(start_page, end_page + 1):
            self.urls.append("https://www.metacritic.com/browse/games/score/userscore/all/filtered?page=" + str(i - 1))
    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)
    def is_gap(self, userScore, metaScore):
        "https://www.metacritic.com/about-metascores"
        userScore = float(userScore)
        metaScore = float(metaScore)
        if userScore >= 7.5:
            userColor = "green"
        elif userScore >= 5.0:
            userColor = "yellow"
        else:
            userColor = "red"
        if metaScore >= 75:
            metaColor = "green"
        elif metaScore >= 50:
            metaColor = "yellow"
        else:
            metaColor = "red"
        if metaColor != userColor and abs(metaScore - userScore * 10) >= 20:
            return True
        return False

    def u_shape(self, positive, mixed, negative):
        total = positive + mixed + negative
        if total == 0:
            return False
        positive_ratio = positive / total
        mixed_ratio = mixed / total
        negative_ratio = negative / total

        if mixed_ratio <= 0.3 and positive_ratio >= 0.3 and negative_ratio >= 0.3:
            return True
        else:
            return False


    def parse(self, response, **kwargs):
        game_links = response.xpath(
            "//table[has-class('clamp-list')]/tr/td[has-class('clamp-summary-wrap')]/a[has-class('title')]/@href").getall()
        pageNum = response.xpath("//ul[has-class('pages')]/li[has-class('active_page')]/span/text()").get()
        # fl.write("page: " + pageNum + ":\n")

        # if not os.path.exists("cache.pickle"):
        #     f = open("cache.pickle", "xb")
        #     f.close()
        #     cache = []
        # else:
        #     with open("cache.pickle", 'rb') as f:
        #         cache = pickle.load(f)
        # for game_link in game_links:
        #     if game_link not in cache:
        #         cache.append(game_link)
        #         yield response.follow(game_link, self.parse_game)
        # with open("cache.pickle", 'wb') as f:
        #     pickle.dump(cache, f)
        summary_wraps = response.xpath("//table[has-class('clamp-list')]/tr/td[has-class('clamp-summary-wrap')]")
        for summary_wrap in summary_wraps:
            name = summary_wrap.xpath("a/h3/text()").get()
            platform = summary_wrap.xpath(
                "div[has-class('clamp-details')]/div[has-class('platform')]/span[has-class('data')]/text()").get().strip()
            releaseDate = summary_wrap.xpath("div[has-class('clamp-details')]/span/text()").get().strip()
            id = self.getId(name, platform, releaseDate)
            conn = mysql.connector.connect(user="kardel", password="alksdj1029a", host="localhost", database="SI507")
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM cache WHERE id='{id}'")
            r = cursor.fetchone()
            if r is None:
                # there is not such a phrase in cache
                print("Doesn't contains")
                game_link = summary_wrap.xpath("a[has-class('title')]/@href").get()
                yield response.follow(game_link, self.parse_game)
                # insertion
                cursor.execute(f"INSERT INTO cache (id) VALUES ('{id}')", )
                conn.commit()
            cursor.close()

    def parse_game(self, response):
        # region basic information: name, summary, platform, publishers, release date
        print("game.url", response.url)
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
        img_url = response.xpath("//img[has-class('product_image')]/@src").get()
        # endregion
        # region scores
        # print("publishers:", publishers)
        metaScore = response.xpath("//div[has-class('metascore_summary')]/div/a/div/span/text()").get()
        userScore = response.xpath("//div[has-class('userscore_wrap')]/a/div/text()").get()
        # print("metaScore:", metaScore)
        # print("userScore:", userScore)
        meta_positiveScore = 0
        meta_mixedScore = 0
        meta_negativeScore = 0
        metaCritics = response.xpath(
            "//div[has-class('critic_reviews_module')]/div[has-class('body')]/div/div/ol/li/div")
        for metaCritic in metaCritics:
            if metaCritic.xpath("span[has-class('label')]/text()").get().startswith("Positive"):
                # print("Positive")
                score = metaCritic.xpath("span[has-class('data')]/a/span/span[has-class('count')]/text()").get()
                if score is not None:
                    meta_positiveScore = int(score.replace(",", ""))
                else:
                    meta_positiveScore = 0
            elif metaCritic.xpath("span[has-class('label')]/text()").get().startswith("Mixed"):
                # print("Mixed")
                score = metaCritic.xpath("span[has-class('data')]/a/span/span[has-class('count')]/text()").get()
                if score is not None:
                    meta_mixedScore = int(score.replace(",", ""))
                else:
                    meta_mixedScore = 0

            elif metaCritic.xpath("span[has-class('label')]/text()").get().startswith("Negative"):
                # print("Negative")
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
                # print("Positive")
                score = metaCritic.xpath("span[has-class('data')]/a/span/span[has-class('count')]/text()").get()
                if score is not None:
                    user_positiveScore = int(score.replace(",", ""))
                else:
                    user_positiveScore = 0
            elif metaCritic.xpath("span[has-class('label')]/text()").get().startswith("Mixed"):
                # print("Mixed")
                score = metaCritic.xpath("span[has-class('data')]/a/span/span[has-class('count')]/text()").get()
                if score is not None:
                    user_mixedScore = int(score.replace(",", ""))
                else:
                    user_mixedScore = 0
            elif metaCritic.xpath("span[has-class('label')]/text()").get().startswith("Negative"):
                # print("Negative")
                score = metaCritic.xpath("span[has-class('data')]/a/span/span[has-class('count')]/text()").get()
                if score is not None:
                    user_negativeScore = int(score.replace(",", ""))
                else:
                    user_negativeScore = 0
        # endregion
        if self.u_shape(user_positiveScore, user_mixedScore, user_negativeScore) or self.is_gap(userScore, metaScore):

            # use basic information of a game as id
            id = self.getId(name, platform, releaseDate)

            # region
            meta_review_link = response.xpath("//div[has-class('metascore_summary')]/div/a/@href").get()
            user_review_link = response.xpath("//div[has-class('userscore_wrap')]/a/@href").get()
            """
             todo:  
             problem Statement: some games with numerous discussion (For example: TLOU2
             `https://www.metacritic.com/game/playstation-4/the-last-of-us-part-ii`, which is a game having 70000+ user
             reviews) will cause a heavy load to me and crawler (Because Metacritic sucks, it even doesn't use AJAX for
             loading remarks. These games cause many approaches ,which work well for many games, works badly for them.
             For example, since Metacritic sucks, we should reload/refresh user review page for many times to reveal these
             remarks. Also, since it could be a heavy load for te database, I only record 2000~3000 remarks uniformally
             from Positive, Mixed and Negative remarks. And according to my observation, many master pieces, which ought
             to have numerous discussion, only have 1000+ remarks. So we don't need to worry whether using a high load/ low
             load strategies will cause bad result)
    
             Condition:  Low Load when the total number of remarks is less than 3000.
                         High Load when the total number of remarks is less than 3000.
    
            Methods: 1. High Load should consider to reload until the page reviews well
                     2. We only takes at most 1000 green (Positive), 1000 (Mixed), 1000 Negative (Negative) reviews.  
             """
            total_reviews_number = user_positiveScore + user_mixedScore + user_negativeScore
            if total_reviews_number > 3000:
                yield response.follow(user_review_link, self.parse_user_review_high_load, meta={"id": id})
            else:
                yield response.follow(user_review_link, self.parse_user_review_low_load, meta={"id": id, "limit": -100})

            yield response.follow(meta_review_link, self.parse_meta_review, meta={"id": id})
            # endregion

            game = gameItem.Game(id=id,
                                 img_url=img_url,
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

            yield game
        else:
            print("escape")

    def getId(self, name, platform, releaseDate):
        id = hashlib.sha256(
            (name + platform + releaseDate).encode("utf-8")).hexdigest()
        return id

    def parse_meta_review(self, response):
        """
        Crawl on the medias' reviews
        sample website: https://www.metacritic.com/game/playstation-4/the-last-of-`us-part-ii/user-reviews?sort-by=score&num_items=100
        :param response: the web page
        :return: Review Item (type=meta, game id is passed from last method)
        """
        print("parse_meta_review.response.url:", response.url)
        game_id = response.meta.get("id")
        print("game id:", game_id)

        all_li = response.xpath("//ol[has-class('critic_reviews')]")[0].xpath("li[has-class('critic_review')]")
        for li in all_li:
            review_section = li.xpath("div/div/div/div/div/div[has-class('review_section')]")[0]
            review_stats = review_section.xpath("div[has-class('review_stats')]")
            review_critics = review_stats.xpath("div[has-class('review_critic')]")
            date = review_critics.xpath("div[has-class('date')]/text()").get()
            if date is None:
                date = "Not Defined"
            print("date:", date)
            source = review_critics.xpath("div[has-class('source')]/text()").get()
            if source is None:
                source = review_critics.xpath("div[has-class('source')]/a/text()").get()
            print("source:", source)
            grade = review_stats.xpath("div[has-class('review_grade')]/div/text()").get()
            grade = int(grade)
            print("grade:", grade)
            review_body = review_section.xpath("div[has-class('review_body')]/text()").get()
            review_body_span = review_section.xpath("div[has-class('review_body')]/span/text()").get()
            review_body_span_expanded = review_section.xpath("div[has-class('review_body')]/span/span[has-class("
                                                             "'blurb_expanded')]/text()").get()
            if review_body_span_expanded is not None:
                body = review_body_span_expanded
            elif review_body_span is not None:
                body = review_body_span
            else:
                body = review_body
            if body is not None:
                body = body.strip()

            yield reviewItem.Review(type="meta", score=grade, date=date, content=body, source=source, game_id=game_id)

    def parse_user_review_low_load(self, response):
        print("parse_user_review_low_load.response.url:", response.url)
        game_id = response.meta.get("id")
        print("game id:", game_id)
        limit = response.meta.get("limit")
        all_li = response.xpath("//ol[has-class('user_reviews')]/li[has-class('user_review')]")
        for li in all_li:
            review_section = li.xpath("div/div/div/div/div/div[has-class('review_section')]")[0]
            review_stats = review_section.xpath("div[has-class('review_stats')]")
            review_critics = review_stats.xpath("div[has-class('review_critic')]")
            date = review_critics.xpath("div[has-class('date')]/text()").get()
            if date is None:
                date = "Not Defined"
            print("date:", date)
            source = review_critics.xpath("div[has-class('name')]/text()").get()
            if source is None or source.strip() == "":
                source = review_critics.xpath("div[has-class('name')]/a/text()").get()
            if source is None or source.strip() == "":
                source = review_critics.xpath("div[has-class('name')]/span/text()").get()
            print("source:", source)
            grade = review_stats.xpath("div[has-class('review_grade')]/div/text()").get()
            grade = float(grade)
            print("grade:", grade)
            review_body = review_section.xpath("div[has-class('review_body')]/text()").get()
            review_body_span = review_section.xpath("div[has-class('review_body')]/span/text()").get()
            review_body_span_expanded = review_section.xpath("div[has-class('review_body')]/span/span[has-class("
                                                             "'blurb_expanded')]/text()").get()
            if review_body_span_expanded is not None:
                body = review_body_span_expanded
            elif review_body_span is not None:
                body = review_body_span
            else:
                body = review_body
            if body is not None:
                body = body.strip()
            print("body:", body)

            if limit != 100:
                next_page_url = response.xpath(
                    "//ul[has-class('pages')]/li[span[has-class('page_num')]]/following-sibling::li[1]/a/@href").get()
                if next_page_url is not None and next_page_url != "":
                    yield response.follow(next_page_url, self.parse_user_review_low_load,
                                          meta={"limit": limit - 100, "id": game_id})

            yield reviewItem.Review(type="user", score=grade, date=date, content=body, source=source, game_id=game_id)

    def parse_user_review_high_load(self, response):
        print("parse_user_review_high_load.response.url:", response.url)
        print("response.url:", response.url)
        game_id = response.meta.get("id")
        all_review_li = response.xpath("//ol[has-class('score_counts')]/li[has-class('score_count')]")
        print(all_review_li)
        positive_link = all_review_li[0].xpath("div[has-class('count_wrap')]/span[has-class('data')]/a/@href").get()
        mixed_link = all_review_li[1].xpath("div[has-class('count_wrap')]/span[has-class('data')]/a/@href").get()
        negative_link = all_review_li[2].xpath("div[has-class('count_wrap')]/span[has-class('data')]/a/@href").get()
        print("positive_link", positive_link)
        print("mixed_link", mixed_link)
        print("negative_link", negative_link)
        yield response.follow(positive_link, self.parse_user_review_low_load, meta={"id": game_id, "limit": 1000})
        yield response.follow(mixed_link, self.parse_user_review_low_load, meta={"id": game_id, "limit": 1000})
        yield response.follow(negative_link, self.parse_user_review_low_load, meta={"id": game_id, "limit": 1000})
