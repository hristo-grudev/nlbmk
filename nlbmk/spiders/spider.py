import scrapy

from scrapy.loader import ItemLoader
from ..items import NlbmkItem
from itemloaders.processors import TakeFirst


class NlbmkSpider(scrapy.Spider):
	name = 'nlbmk'
	start_urls = ['https://nlb.mk/%D0%97%D0%B0_%D0%91%D0%B0%D0%BD%D0%BA%D0%B0%D1%82%D0%B0/%D0%97%D0%B0_%D0%BC%D0%B5%D0%B4%D0%B8%D1%83%D0%BC%D0%B8%D1%82%D0%B5/%D0%A1%D0%BE%D0%BE%D0%BF%D1%88%D1%82%D0%B5%D0%BD%D0%B8%D1%98%D0%B0_%D0%B7%D0%B0_%D1%98%D0%B0%D0%B2%D0%BD%D0%BE%D1%81%D1%82.aspx']

	def parse(self, response):
		post_links = response.xpath('//div[@class="page-container container-fluid "]/div/div/div/div')
		for post in post_links:
			date = post.xpath('./div[@class="col-sm-2 date"]/text()').get()
			url = post.xpath('./div[@class="col-sm-10 link"]/a/@href').get()
			yield response.follow(url, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//div[@class="pagination pagination__posts"]/ul/li[@class="next"]/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)


	def parse_post(self, response, date):
		title = response.xpath('//div[@class="holder mark col-md-12"]/h1//text()').get()
		description = response.xpath('//div[@class="holder mark col-md-12"]//text()[normalize-space() and not(ancestor::h1)]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=NlbmkItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
