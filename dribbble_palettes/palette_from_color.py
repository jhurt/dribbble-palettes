import argparse
import os
import scrapy
import shutil

from PIL import Image
from scrapy.crawler import CrawlerProcess

parse_color_results = []


class DribbbleColorSpider(scrapy.Spider):
    """Crawl a dribbble color URL and extract shot information (i.e. shots containing that color),
    then crawl each shot URL and extract the color palette for the shot."""
    name = 'dribble_color_spider'

    def parse(self, response):
        shots_xpath = '//div[@id="main"]/ol[@class="dribbbles group"]/li//a[@class="dribbble-link"]/@href'
        for href in response.xpath(shots_xpath).extract():
            full_url = 'https://dribbble.com' + href
            yield scrapy.Request(full_url, callback=self.parse_hex_colors)

    def parse_hex_colors(self, response):
        hex_xpath = '//ul[@class="color-chips group"]/li[@class="color"]/a/@title'
        yield {
            'hex': response.xpath(hex_xpath).extract()
        }


class DribbbleColorPipeline(object):
    def process_item(self, item, spider):
        parse_color_results.append(dict(item))


def hex_to_rgb(value):
    """taken from: http://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa"""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def cli():
    parser = argparse.ArgumentParser(description='''Creates palettes given a hex color.''')

    parser.add_argument('-hex',
                        dest='hex_color',
                        required=True,
                        help='The starting hex color to create a palette from.')
    args = parser.parse_args()

    dribbble_color_url = 'https://dribbble.com/colors/' + args.hex_color

    # crawl dribbble for palettes related to the color
    dribble_color_crawler = CrawlerProcess({
        'ITEM_PIPELINES': {'__main__.DribbbleColorPipeline': 1}
    })
    dribble_color_crawler.crawl(DribbbleColorSpider, start_urls=[dribbble_color_url])
    dribble_color_crawler.start()  # block here until the crawling is finished

    # combine all palette colors from all shot pages
    palette_colors = set()
    for item in parse_color_results:
        for color_hex in item['hex']:
            palette_colors.add(color_hex)

    # remove any previous output for this color url
    color_dir = 'palettes' + os.path.sep + args.hex_color
    if os.path.isdir(color_dir):
        shutil.rmtree(color_dir)
    os.mkdir(color_dir)

    # create a square image of each color in the palette
    for color in palette_colors:
        color_hex_image = Image.new('RGB', (50, 50), hex_to_rgb(color))
        color_hex_image.save(color_dir + os.path.sep + color[1:].lower() + '.png')

    print "Generated palette colors for " + args.hex_color + " in " + color_dir

if __name__ == "__main__":
    cli()
