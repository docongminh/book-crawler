import scrapy
from bs4 import BeautifulSoup
from scrapy_splash import SplashRequest
import re
import os
import io
from PIL import Image
import requests


data = 'all_data'

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
    name = "book"

    def start_requests(self):
        urls = [
                "http://nhanam.com.vn//sach-moi-xuat-ban",
                "http://nhanam.com.vn//chuyen-muc/1/van-hoc-viet-nam",
                "http://nhanam.com.vn//chuyen-muc/2/tieu-thuyet",
                "http://nhanam.com.vn//chuyen-muc/3/truyen-ngan",
                "http://nhanam.com.vn//chuyen-muc/4/tho-kich",
                "http://nhanam.com.vn//chuyen-muc/5/hoi-ky-phe-binh-tieu-luan",
                "http://nhanam.com.vn//chuyen-muc/6/tap-but-tan-van",
                "http://nhanam.com.vn//chuyen-muc/7/van-hoc-nuoc-ngoai",
                "http://nhanam.com.vn//chuyen-muc/8/duong-dai",
                "http://nhanam.com.vn//chuyen-muc/9/lang-man",
                "http://nhanam.com.vn//chuyen-muc/10/trinh-tham-kinh-di",
                "http://nhanam.com.vn//chuyen-muc/11/kiem-hiep",
                "http://nhanam.com.vn//chuyen-muc/12/kinh-dien",
                "http://nhanam.com.vn//chuyen-muc/13/tho-kich",
                "http://nhanam.com.vn//chuyen-muc/14/hoi-ky-tieu-luan",
                "http://nhanam.com.vn//chuyen-muc/15/huyen-ao-gia-tuong",
                "http://nhanam.com.vn//chuyen-muc/16/tan-van-tap-but",
                "http://nhanam.com.vn//chuyen-muc/17/thieu-nhi",
                "http://nhanam.com.vn//chuyen-muc/18/tuoi-teen",
                "http://nhanam.com.vn//chuyen-muc/19/truyen-tranh",
                "http://nhanam.com.vn//chuyen-muc/20/thieu-nhi",
                "http://nhanam.com.vn//chuyen-muc/21/thoi-su---chinh-tri",
                "http://nhanam.com.vn//chuyen-muc/22/hoi-ky-tu-truyen",
                "http://nhanam.com.vn//chuyen-muc/23/the-gioi-hien-dai",
                "http://nhanam.com.vn//chuyen-muc/25/khoa-hoc-tu-nhien---nhan-van",
                "http://nhanam.com.vn//chuyen-muc/26/lich-su",
                "http://nhanam.com.vn//chuyen-muc/27/triet-hoc",
                "http://nhanam.com.vn//chuyen-muc/28/tam-ly-hoc",
                "http://nhanam.com.vn//chuyen-muc/29/kinh-te",
                "http://nhanam.com.vn//chuyen-muc/30/vu-tru",
                "http://nhanam.com.vn//chuyen-muc/31/sinh-hoc",
                "http://nhanam.com.vn//chuyen-muc/32/tham-khao",
                "http://nhanam.com.vn//chuyen-muc/43/giam-gia-dac-biet",
                "http://nhanam.com.vn//chuyen-muc/44/sach-tai-ban",
                "http://nhanam.com.vn//chuyen-muc/45/dat-truoc-sach",


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
            yield SplashRequest(url=url, endpoint = "render.html", callback=self.parse_detail)
    
    def parse_detail(self, response):
        """
            parse detail in each item
        """
        for book in response.xpath('/html/body/div[1]/div[3]/ul/li'):
            link_down_book = book.css("a").css('img::attr(src)').extract_first()
            name = link_down_book.split("/")[-1]
            path = data + '/' + name
            check_exist(data)
            download_image(link_down_book, path)


        next_page = response.css('div .pager').css('a[class=next]::attr(href)').extract_first()
        print(next_page)
        if next_page is not None :
            next_link = "http://nhanam.com.vn" + next_page
            with open("next_link.txt", 'a') as f:
                f.write(next_link)
                f.write('\n')
            yield scrapy.Request(next_link, callback=self.parse_detail)

