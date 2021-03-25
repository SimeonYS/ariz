import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import ArizItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class ArizSpider(scrapy.Spider):
	name = 'ariz'
	start_urls = ['https://www.arizbank.com/customer-service/about/news']

	def parse(self, response):
		post_links = response.xpath('//li[@class="medium-4 cell"]/a[1]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li[@class="pager-next"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		try:
			date = response.xpath('//div[@class="cell medium-7"]/p/strong/text() | //div[@class="content"]/p/strong/text() | //div[@class="abt"]/div[2]/p[1]/text() | //div[@class="content"]/h3[2]//text()').get()
			date = re.findall(r'\w+\s\d+\,\s\d+',date)
		except AttributeError:
			date = ""
		title = ''.join(response.xpath('//h1//text()').getall()).strip()
		content = response.xpath('//div[@class="cell medium-7"]//text() | //div[@class="content"]//text() | //div[@class="abt"]/div[2]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=ArizItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
