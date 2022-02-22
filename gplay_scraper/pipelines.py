# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sqlite3
from itemadapter import ItemAdapter


class GplayScraperPipeline:
    def __init__(self):
        # db setup
        self.create_connection()
        self.load_prod_number_prod_price_pairs()
        self.load_categories()
        self.load_subcategories()

    def create_connection(self):
        """connect to the DB"""
        self.conn = sqlite3.connect("gplay_store.db")
        self.curr = self.conn.cursor()

    def load_prod_number_prod_price_pairs(self):
        """Load pairs of product number at the product price in a dictionary"""
        self.curr.execute("SELECT product_number, product_price FROM products")
        self.products_num_price = dict(self.curr.fetchall())

    def load_categories(self):
        """Load all categories into a list"""
        self.curr.execute("SELECT category_title FROM categories")
        self.categories = self.curr.fetchall()
        self.categories = [c[0] for c in self.categories]

    def load_subcategories(self):
        """Load all subcategories into a list"""
        self.curr.execute("SELECT subcategory_title FROM subcategories")
        self.subcategories = self.curr.fetchall()
        self.subcategories = [sc[0] for sc in self.subcategories]

    def process_item(self, item, spider):
        """Process a single product, filtered and save only new categories, subcategories and product. Update changed prices"""

        if not self.item_in_db(item):
            # Save only item in this categories
            if item["category"] in ["Гейминг периферия", "Гейминг хардуер"]:
                self.save_item(item)
            return item

        if not self.item_price_changed(item):
            return item

        self.update_item(item)

        return item

    def item_in_db(self, item) -> bool:
        """Check if the produst is in DB"""
        if item["product_number"] in self.products_num_price.keys():
            return True
        return False

    def save_item(self, item) -> bool:
        """Save the product in DB"""
        subcategory_id = self.get_item_subcategory_id(item)
        title = item["title"]
        subtitle = item["subtitle"]
        product_number = item["product_number"]
        price = item["price"]

        self.curr.execute(
            f"""
            INSERT INTO products (
                ID_subcategory,
                product_title,
                product_subtitle,
                product_number,
                product_price
            )
            VALUES
            (
                {subcategory_id},
                '{title}',
                '{subtitle}',
                '{product_number}',
                {price}
            )
            """
        )
        self.conn.commit()
        return True

    def item_price_changed(self, item):
        """Return true if the price has changed"""
        if item["price"] == self.products_num_price[item["product_number"]]:
            return False
        return True

    def update_item(self, item):
        """Update the item price"""
        self.curr.execute(
            f"""
            UPDATE products
                SET
                    product_price = '{item["price"]}'
                WHERE
                    product_number = '{item["product_number"]}'
            """
        )
        self.conn.commit()
        self.products_num_price[item["product_number"]] = item["price"]
        pr = self.products_num_price[item["product_number"]]

    def get_item_category_id(self, item):
        """Return the ID of items category"""
        category = item["category"]
        if not category in self.categories:
            self.insert_new_category(category)
            self.categories.append(category)

        self.curr.execute(
            f"""
            SELECT
                category_ID
            FROM
                categories
            WHERE
                category_title = '{category}'
            """
        )
        category_id = self.curr.fetchone()[0]
        return category_id

    def insert_new_category(self, category):
        """Insert new category in DB"""
        self.curr.execute(
            f"""
            INSERT OR IGNORE INTO categories (category_title) VALUES ('{category}')
            """
        )
        self.conn.commit()

    def get_item_subcategory_id(self, item):
        """Return the ID of items subcategory"""
        subcategory = item["subcategory"]
        if not subcategory in self.subcategories:
            self.insert_new_subcategory(
                self.get_item_category_id(item), subcategory
            )
            self.subcategories.append(subcategory)

        self.curr.execute(
            f"""
            SELECT
                subcategory_ID
            FROM
                subcategories
            WHERE
                subcategory_title = '{subcategory}'
            """
        )
        subcategory_id = self.curr.fetchone()[0]
        return subcategory_id

    def insert_new_subcategory(self, category_id, subcategory):
        """Insert new subcategory in DB"""
        self.curr.execute(
            f"""
            INSERT OR IGNORE INTO subcategories
                (ID_category, subcategory_title)
            VALUES
                ({category_id}, '{subcategory}')
            """
        )
        self.conn.commit()

