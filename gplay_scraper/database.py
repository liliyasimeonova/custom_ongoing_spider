import sqlite3

conn = sqlite3.connect("gplay_store.db")
curr = conn.cursor()


curr.execute(
    """
    CREATE TABLE categories(
        category_ID INTEGER PRIMARY KEY,
        category_title TEXT UNIQUE NOT NULL
    )
    """
)

curr.execute(
    """
    CREATE TABLE subcategories(
        subcategory_ID INTEGER PRIMARY KEY,
        ID_category INTEGER NOT NULL,
        subcategory_title TEXT UNIQUE NOT NULL,

        FOREIGN KEY (ID_category)
            REFERENCES categories (category_ID)
    )
    """
)

curr.execute(
    """
    CREATE TABLE products(
        product_ID INTEGER PRIMARY KEY,
        ID_subcategory INTEGER NOT NULL,
        product_title TEXT NOT NULL,
        product_subtitle TEXT NOT NULL,
        product_number TEXT UNIQUE NOT NULL,
        product_price FLOAT,
        
        FOREIGN KEY (ID_subcategory)
            REFERENCES categories (subcategory_ID)
    )
    """
)


conn.commit()
conn.close()