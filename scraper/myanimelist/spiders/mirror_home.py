# -*- coding: utf-8 -*-
import scrapy
from myanimelist.items import Mirror


class MirrorHomeSpider(scrapy.Spider):
    name = 'mirror_home'
    allowed_domains = ['animerush.tv']
    start_urls = [
        'http://www.animerush.tv/latest-anime-episodes/',
    ]

    def parse(self, response):
        for episode in response.xpath('//ol[@class="list"]/div/ol/a/@href').extract():
            yield scrapy.Request('http://www.animerush.tv' + episode, callback=self.parse_episode)

    def parse_episode(self, response):
        for mirror in response.xpath('//*[@id="episodes"]/div/div/span/a/@href').extract():
            yield scrapy.Request(mirror, callback=self.parse_mirror)

    @staticmethod
    def parse_mirror(response):
        item = Mirror()
        website = response.xpath('//div[@class="episode_on"]/div/h3/a/text()').extract()
        if (website and any(word in website[0] for word in ['Dailymotion', 'Goplayer', 'COM', 'Videobb'])) \
            or not website or response.xpath('//a[@class="active"]/text()').extract():
            yield item
        else:
            item['url'] = response.xpath(
                '//div[@id="embed_holder"]/div/iframe/@src | //div[@id="embed_holder"]/div/embed/@src | ' +
                '//div[@id="embed_holder"]/div/center/iframe/@src | //div[@id="embed_holder"]/div/div/embed/@src'
            ).extract()[0]
            if 'animerush' not in item['url']:
                item['website'] = website[0].replace('s Video', '').replace('HD Video', '').replace(' Video', '')
                item['anime'] = response.xpath('(//*[@id="left-column"]/div)[last()]/b/text()').extract()[0]
                item['episode'] = response.xpath('//h1/text()').extract()[0].split(item['anime'] + ' Episode ')[1]
                item['translation'] = response.xpath(
                    '//div[@class="episode_on"]/div/span[2]/text()').extract()[0].lower()
                date = response.xpath('//div[@class="episode_on"]/div/span[3]/text()').extract()
                if date:
                    item['date'] = date[0]
                else:
                    item['date'] = None
                if response.xpath('//div[@class="episode_on"]/div/div/img/@alt').extract():
                    item['quality'] = 'HD'
                else:
                    item['quality'] = 'SD'
                yield item
            else:
                yield item
