import scrapy

class QuotesSpider(scrapy.Spider):
    name = "jumia"

    def start_requests(self):
        urls = [
            'https://www.jumia.co.ke/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        navbar = response.css('.main-category')
        categories = []
        for item in navbar:
            category = {
                'name': item.css('span::text').get(),
                'link': item.css('::attr(href)').get()
            }
            categories.append(category)
        for category in categories:
            try:
                yield response.follow(category['link'], callback=self.parse_products)
            except:
                pass

    def parse_products(self, response):
        products = response.css('.sku')
        for product in products:
            try:
                price = product.css('.price-container span::text').getall()
                old_price = price[-3].replace(',', '')
                new_price = price[4].replace(',', '')
                image = product.css('img::attr(src)').getall()
                link = product.css('a::attr(href)').get()
                for im in image:
                    if im.find('http') != -1:
                        image = im
                discount = int(old_price)-int(new_price)
                if discount:
                    yield{
                           'name': product.css('h2 .name::text').get(),
                            'old_price': old_price,
                            'new_price': new_price,
                            'image': image,
                            'link': link,
                            'discount': discount
                    }
            except Exception as e:
                print(e,'\n\n\n\n\n\n\n\n\n\n')
                continue
        next_page = response.css('.pagination a[title="Next"] ::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_products)
