# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BookSpiderItem(scrapy.Item):
    title = scrapy.Field()
    image = scrapy.Field()
    type = scrapy.Field()
    status = scrapy.Field()
    book_desc = scrapy.Field()
    download_url = scrapy.Field()
    id = scrapy.Field()
    author = scrapy.Field()


class AuthorSpiderItem(scrapy.Item):
    id = scrapy.Field()
    author = scrapy.Field()


class ChapterSpiderItem(scrapy.Item):
    content = scrapy.Field()
    title = scrapy.Field()
    sort_num = scrapy.Field()
    book_id = scrapy.Field()
