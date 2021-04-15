import scrapy

from SI507Final.items import gameItem


class AllGameSpider(scrapy.Spider):
    name = "all_games"

    def start_requests(self):
        urls = ["https://www.metacritic.com/browse/games/score/userscore/all/filtered"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):

        game_links = response.xpath("//table[has-class('clamp-list')]/tr/td[has-class('clamp-summary-wrap')]/a[has-class('title')]/@href").getall()
        yield from response.follow_all(game_links, self.parse_game)
        next_page = response.xpath("//ul[has-class('pages')]/li[has-class('active_page')]/following-sibling::node()/a/@href").get()
        yield response.follow(next_page, self.parse)
    def parse_game(self, response):
        print(response.url)
        game_name = response.xpath("//div[has-class('product_title')]/a/h1/text()").get()
        platform = response.xpath("//span[has-class('platform')]/text()").get().strip()
        try:
            summary = response.xpath("//span[has-class('blurb_expanded')]/text()").get().strip()
        except AttributeError:
            summary = response.xpath("//span[has-class('data')]/span/text()").get().strip()
        publisher = response.xpath("//li[has-class('publisher')]/span[has-class('data')]/a/text()").get().strip()
        game = gameItem.Game(name = game_name, summary=summary, platform=platform, publisher=publisher)

        return game