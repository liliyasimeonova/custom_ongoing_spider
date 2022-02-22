from gc import callbacks
import scrapy
import re


class Categories(scrapy.Spider):
    name = "categories"
    start_urls = [
        "https://gplay.bg/%D0%B3%D0%B5%D0%B9%D0%BC%D0%B8%D0%BD%D0%B3-%D0%BF%D0%B5%D1%80%D0%B8%D1%84%D0%B5%D1%80%D0%B8%D1%8F",
        "https://gplay.bg/%D0%B3%D0%B5%D0%B9%D0%BC%D0%B8%D0%BD%D0%B3-%D1%85%D0%B0%D1%80%D0%B4%D1%83%D0%B5%D1%80",
    ]

    def parse(self, response):
        """Parses trough categories"""
        subcategories = response.xpath(
            "//div[@class='categories-grid-item']//a/@href"
        ).getall()
        for _subcategory in subcategories:
            _subcategory = (
                _subcategory + "?prices%5B0%5D=0.00&prices%5B1%5D=200.00"
            )
            yield response.follow(
                _subcategory, callback=self.parse_subcategory
            )

    def parse_subcategory(self, response):
        """Parse trough subcategory"""
        pages = response.xpath("//a[@class='page-link']//@href").getall()
        for _page in pages:
            yield response.follow(_page, callback=self.parse_pages)

    def parse_pages(self, response):
        """Parse trough pages"""
        products = response.xpath(
            "//div[@class='product-item']//a/@href"
        ).getall()
        for _product in products:
            yield response.follow(_product, callback=self.parse_product)

    def parse_product(self, response):
        """Parse trough product"""
        _categories = response.xpath(
            "//div[@class='path py-3']//a//text()"
        ).getall()
        category = _categories[1].strip()
        subcategory = _categories[2].strip()
        _product = response.xpath(
            "//div[@class='col-xxl-7 col-xl-6']|(//div[@class='container py-5'])[1]",
        )
        title = _product.xpath("//h1//text()").get().strip()
        try:
            subtitle = _product.xpath("//h2//text()").get().strip()
        except:
            subtitle = (
                _product.xpath("//div[@class='product-subtitle']//text()")
                .get()
                .strip()
            )
        product_number = _product.xpath(
            "//div[@class='col-md-6 product-ref-number']//strong//text()"
        ).get()
        price = _product.xpath("//div[@class='price']").get()
        # if price of product is not adjustable, edge case
        if not price:
            price = -1
        else:
            pattern = r'<price :price="(\d+(\.\d+)?)"></price>'
            price = round(float(re.search(pattern, price).group(1)), 2)

        data = {
            "category": category,
            "subcategory": subcategory,
            "title": title,
            "subtitle": subtitle,
            "product_number": product_number,
            "price": price,
        }
        yield data

