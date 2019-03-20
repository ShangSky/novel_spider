# -*- coding: utf-8 -*-
import requests
from datetime import datetime
from twisted.enterprise import adbapi
from book_spider.items import BookSpiderItem, ChapterSpiderItem, AuthorSpiderItem


class BookSpiderPipeline(object):
    def __init__(self):
        dbparams = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': '11111',
            'password': '111111',
            'database': 'book_city',
            'charset': 'utf8'
        }
        self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        self.book_sql = '''insert into book_book(id, create_time, update_time, 
        image, title, `type`, collect_num, click_num, comment_num, recommend_num,
        `desc`, download_url, author_id, status) values (%s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s)'''
        self.author_sql = '''insert into author_author(id, create_time, update_time,
        name, `desc`, attention_num, avatar) values (%s, %s, %s, %s, %s, %s, %s)'''
        self.chapter_sql = '''insert into book_chapter(id, create_time, update_time,
         title, content, book_id, sort_number) values (null, %s, %s, %s, %s, %s, %s) '''
        self.foreign_sql = 'SET FOREIGN_KEY_CHECKS=0'
        self.select_author_sql = 'select * from author_author where name=%s'

    def process_item(self, item, spider):
        if isinstance(item, BookSpiderItem):
            self.dbpool.runInteraction(self.insert_book_item, item)
        if isinstance(item, AuthorSpiderItem):
            self.dbpool.runInteraction(self.insert_author_item, item)
        if isinstance(item, ChapterSpiderItem):
            self.dbpool.runInteraction(self.insert_chapter_item, item)
        return item

    def insert_book_item(self, cursor, item):
        image_path = 'book/{}.jpg'.format(item['title'])
        with open(image_path, 'wb') as f:
            f.write(requests.get(item['image']).content)
        cursor.execute(self.foreign_sql)
        cursor.execute(self.select_author_sql, (item['author']))
        data = cursor.fetchall()
        if data:
            author_id = data[0][0]
        else:
            author_id = item['id']
        cursor.execute(self.book_sql, (
            item['id'], datetime.now(), datetime.now(), image_path,
            item['title'], item['type'], 0, 0, 0, 0, item['book_desc'],
            item['download_url'], author_id, item['status']
        ))
        print('书本信息导入成功')

    def insert_author_item(self, cursor, item):
        avatar_path = 'author/avatar.jpg'
        desc = '其文字风格细腻，架构有序，情节跌宕，内涵深刻。想象力超绝，行文如天马行空，超脱不羁，能最大程度调动读者的代入感和心理欲求，其亦庄亦谐，纤秾合度的笔法也使读者们欲罢不能！'
        cursor.execute(self.select_author_sql, (item['author']))
        data = cursor.fetchall()
        if data:
            print('已有作者信息')
        else:
            cursor.execute(self.author_sql, (item['id'], datetime.now(), datetime.now(), item['author'], desc, 0, avatar_path))
            print('作者信息导入成功')

    def insert_chapter_item(self, cursor, item):
        cursor.execute(self.foreign_sql)
        cursor.execute(self.chapter_sql, (datetime.now(), datetime.now(), item['title'], item['content'], item['book_id'], item['sort_num']))
        print('章节信息导入成功')
