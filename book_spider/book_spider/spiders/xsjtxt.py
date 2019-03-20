# -*- coding: utf-8 -*-
import re
import scrapy
from book_spider.items import BookSpiderItem, ChapterSpiderItem, AuthorSpiderItem
from random import randint


class XsjtxtSpider(scrapy.Spider):
    name = 'xsjtxt'
    allowed_domains = ['xsjtxt.com']
    start_urls = [
        'https://www.xsjtxt.com/soft/1/Soft_001_1.html',
        'https://www.xsjtxt.com/soft/2/Soft_002_1.html',
        'https://www.xsjtxt.com/soft/3/Soft_003_1.html',
        'https://www.xsjtxt.com/soft/4/Soft_004_1.html',
        'https://www.xsjtxt.com/soft/5/Soft_005_1.html',
        'https://www.xsjtxt.com/soft/6/Soft_006_1.html',
        'https://www.xsjtxt.com/soft/7/Soft_007_1.html',
        'https://www.xsjtxt.com/soft/9/Soft_009_1.html',
        'https://www.xsjtxt.com/soft/10/Soft_010_1.html',
        'https://www.xsjtxt.com/soft/12/Soft_012_1.html',
        'https://www.xsjtxt.com/soft/14/Soft_014_1.html',
    ]

    def parse(self, response):
        li_list = response.xpath("//div[@class='list']//ul/li")
        for li in li_list:
            href = 'https://www.xsjtxt.com' + li.xpath("./a/@href").extract_first()
            yield scrapy.Request(
                url=href,
                callback=self.parse_detail
            )
        next_url = response.xpath("//a[text()='下一页']/@href").extract_first()
        page_num = re.findall(r'/soft/\d+/Soft_\d+_(\d+).html', next_url)
        if int(page_num[0]) <= 5:
            next_url = 'https://www.xsjtxt.com' + next_url
            yield scrapy.Request(next_url)

    def parse_detail(self, response):
        type_dict = {
            '武侠小说': 'wx',
            '玄幻小说': 'xh',
            '都市言情': 'ds',
            '恐怖灵异': 'kb',
            '现代文学': 'xd',
            '侦探推理': 'zt',
            '科幻小说': 'kh',
            '穿越架空': 'cy',
            '古典名著': 'gd',
            '历史军事': 'ls',
            '网游小说': 'wy'
        }

        book_item = BookSpiderItem()
        author_item = AuthorSpiderItem()
        book_item['title'] = response.xpath("//div[@class='detail_right']/h1/text()").extract_first().replace('全集下载', '').replace('《', '').replace('》', '')
        book_item['image'] = 'https://www.xsjtxt.com' + response.xpath("//div[@class='detail_pic']/img/@src").extract_first()
        book_item['type'] = type_dict[response.xpath("//div[@class='wrap position']/span/a[2]/text()").extract_first()]
        book_item['status'] = randint(0, 1)
        author_item['author'] = response.xpath("//div[@class='detail_right']/ul/li[6]/text()").extract_first().replace('书籍作者：', '')
        book_item['author'] = author_item['author']
        book_item['book_desc'] = response.xpath("//div[@class='showInfo']/p/text()").extract_first().replace(' ', '').replace('\u3000', '')
        download_url = response.xpath("//div[@class='showDown']/ul/li[3]/script/text()").extract_first()
        if download_url:
            download_url = eval(download_url.replace('get_down_url', '').replace(';', ''))[1]
        else:
            download_url = ''
        book_item['download_url'] = download_url

        chapter_url = 'https://www.xsjtxt.com' + response.xpath("//div[@class='showDown']/ul/li[1]/a/@href").extract_first()
        book_item['id'] = re.findall(r'https://www.xsjtxt.com/book/(\d+)/', chapter_url)[0]
        author_item['id'] = book_item['id']
        yield book_item
        yield author_item
        yield scrapy.Request(
            chapter_url,
            callback=self.parse_chapter,
        )

    def parse_chapter(self, response):
        chapter_list = response.xpath("//div[@id='info'][3]/div[@class='pc_list']/ul/li")
        for index, chapter in enumerate(chapter_list[:50]):
            item = ChapterSpiderItem()
            item['title'] = chapter.xpath("./a/text()").extract_first()
            item['sort_num'] = index
            url = response.url + chapter.xpath("./a/@href").extract_first()
            item['book_id'] = re.findall(r'https://www.xsjtxt.com/book/(\d+)/', response.url)[0]
            yield scrapy.Request(
                url,
                self.parse_chapter_detail,
                meta={'item': item}
            )

    def parse_chapter_detail(self, response):
        item = response.meta['item']
        item['content'] = re.findall(r'<div\s+id="content1".*?>\s+(.*?)</div>', response.text, re.DOTALL)[0]
        yield item
