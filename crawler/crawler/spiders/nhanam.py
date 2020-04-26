import scrapy
from bs4 import BeautifulSoup
from scrapy_splash import SplashRequest
import re
import os
import io
from PIL import Image
import requests


data = 'data'

def check_exist(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        print(e)
        pass


def download_image(url, image_file_path):
    r = requests.get(url, timeout=4.0)
    if r.status_code != requests.codes.ok:
        assert False, 'Status code error: {}.'.format(r.status_code)

    with Image.open(io.BytesIO(r.content)) as im:
        im.save(image_file_path, format='JPEG')

    print('Image downloaded from url: {} and saved to: {}.'.format(url, image_file_path))


class BookCover(scrapy.Spider):
    name = "book-cover"

    def start_requests(self):
        urls = [
                "http://nhanam.com.vn/"

        ]
        script = """
        function main(splash)
            local url = splash.args.url
            assert(splash:go(url))
            assert(splash:wait(0.5))
            assert(splash:runjs("$('.next')[0].click();"))
            return {
                html = splash:html(),
                url = splash:url(),
            }
        end
        """
        for url in urls:
            yield SplashRequest(url=url, endpoint = "render.html", callback=self.parse)
    
    def parse_detail(self, response):
        """
            parse detail in each item
        """
        try:
            item = response.request.meta['item']
            print(">>>book: ", len(response.xpath('/html/body/div[1]/div[3]/ul/li')))
            for book in response.xpath('/html/body/div[1]/div[3]/ul/li'):
                link_down_book = book.css("a").css('img::attr(src)').extract_first()
                name = link_down_book.split("/")[-1]
                path = item['folder'] + '/' + name
                download_image(link_down_book, path)


            next_page = response.css('div .pager').css('a[class=next]::attr(href)').extract_first()
            if next_page is not None :
                next_link = "http://nhanam.com.vn" + next_page
                yield response.follow(next_link, callback=self.parse_detail)
        except Exception as e:
            with open('logs_detail.txt', 'a') as f:
                f.write(str(e))
                f.write('\n')
            pass



    def parse(self, response):
        """
        
        """  
        try:   
            for item in response.xpath('//*[@id="mainnav"]/div/ul/li[1]'):
                for link in item.css('a::attr(href)').extract():
                    path = data + link
                    check_exist(path)
                    full_link = "http://nhanam.com.vn/" + link
                    itemCrawl = {
                        'folder': path,
                        'link': full_link
                    }
                    with open("parse_full_link.txt", 'a') as f:
                        f.write(str(full_link))
                        f.write("\n")
                    yield response.follow(full_link, callback=self.parse_detail,
                        meta={'item':itemCrawl}) # pass itemCrawl here to get more detail
        except Exception as e:
            with open('logs_parse.txt', 'a') as f:
                f.write(str(e))
                f.write('\n')
            pass