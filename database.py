import json
import secrets
import sqlite3
import traceback
from datetime import datetime

import config


class Database:

    @staticmethod
    def initialize():
        """
        データベースを初期化します
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS ticket_buttons(guild_id INTEGER, channel_id INTEGER, message_id INTEGER PRIMARY KEY, role_id INTEGER, category_id INTEGER, first_message TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS semi_vendings(id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id INTEGER, name TEXT, link_channel_id INTEGER, performance_channel_id INTEGER, buyer_role INTEGER, created_at TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS semi_vending_products(vending_id INTEGER, product_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, price INTEGER, created_at TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS semi_vending_stocks(stock_id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, value TEXT, status INTEGER, created_at TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS semi_vending_orders(order_id INTEGER PRIMARY KEY, user_id INTEGER, vending_id INTEGER, product_id INTEGER, stock_id JSON, total INTEGER, created_at TEXT)")
        conn.commit()
        conn.close()

    @staticmethod
    def get_connection():
        """
        コネクションを取得します

        :return: Connection
        """

        return sqlite3.connect(config.DATABASE_NAME)

    class TicketButton:
        def __init__(self, guild_id: int, channel_id: int, message_id: int, role_id: int,
                     category_id: int, first_message: str):
            self.guild_id = guild_id
            self.channel_id = channel_id
            self.message_id = message_id
            self.role_id = role_id
            self.category_id = category_id
            self.first_message = first_message

        @staticmethod
        def create(guild_id: int, channel_id: int, message_id: int, role_id: int, category_id: int,
                   first_message: str):
            conn = Database.get_connection()
            cur = conn.cursor()

            sql = "INSERT INTO ticket_buttons VALUES(?, ?, ?, ?, ?, ?)"
            cur.execute(sql,
                        (guild_id, channel_id, message_id, role_id, category_id, first_message))

            conn.commit()
            conn.close()

        @staticmethod
        def get_all():
            conn = Database.get_connection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            sql = "SELECT * FROM ticket_buttons"
            cur.execute(sql)

            results = cur.fetchall()
            if not results:
                return None

            return [Database.TicketButton(
                result["guild_id"],
                result["channel_id"],
                result["message_id"],
                result["role_id"],
                result["category_id"],
                result["first_message"],
            ) for result in results]

    class SemiVending:
        def __init__(self, id: int, guild_id: int, name: str, link_channel_id: int,
                     performance_channel_id: int, buyer_role: int, created_at: datetime):
            self.id = id
            self.guild_id = guild_id
            self.name = name
            self.link_channel_id = link_channel_id
            self.performance_channel_id = performance_channel_id
            self.buyer_role = buyer_role
            self.created_at = created_at

        def set_link_channel_id(self, link_channel_id: int):
            conn = Database.get_connection()
            cur = conn.cursor()

            sql = "UPDATE semi_vendings SET link_channel_id = ? WHERE id = ?"
            cur.execute(sql, (link_channel_id, self.id))

            conn.commit()
            conn.close()

        def set_performance_channel_id(self, performance_channel_id: int):
            conn = Database.get_connection()
            cur = conn.cursor()

            sql = "UPDATE semi_vendings SET performance_channel_id = ? WHERE id = ?"
            cur.execute(sql, (performance_channel_id, self.id))

            conn.commit()
            conn.close()

        def set_buyer_role_id(self, buyer_role_id: int):
            conn = Database.get_connection()
            cur = conn.cursor()

            sql = "UPDATE semi_vendings SET buyer_role = ? WHERE id = ?"
            cur.execute(sql, (buyer_role_id, self.id))

            conn.commit()
            conn.close()

        def rename(self, name: str):
            conn = Database.get_connection()
            cur = conn.cursor()

            sql = "UPDATE semi_vendings SET name = ? WHERE id = ?"
            cur.execute(sql, (name, self.id))

            conn.commit()
            conn.close()

        def delete(self):
            conn = Database.get_connection()
            cur = conn.cursor()

            sql = "DELETE FROM semi_vendings WHERE id = ?"
            cur.execute(sql, (self.id,))

            conn.commit()
            conn.close()

        @property
        def products(self):
            return Database.SemiVendingProduct.get(self.id)

        @staticmethod
        def create(guild_id: int, name: str):
            conn = Database.get_connection()
            cur = conn.cursor()

            now = datetime.now().replace(microsecond=0)
            sql = "INSERT INTO semi_vendings(guild_id, name, created_at) VALUES(?, ?, ?)"
            cur.execute(sql, (guild_id, name, str(now)))

            conn.commit()
            conn.close()

        @staticmethod
        def get(id: int):
            conn = Database.get_connection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            sql = "SELECT * FROM semi_vendings WHERE id = ?"
            cur.execute(sql, (id,))

            result = cur.fetchone()
            if not result:
                return None

            return Database.SemiVending(
                result["id"],
                result["guild_id"],
                result["name"],
                result["link_channel_id"],
                result["performance_channel_id"],
                result["buyer_role"],
                datetime.strptime(result["created_at"], "%Y-%m-%d %H:%M:%S"),
            )

        @staticmethod
        def get_by_guild(guild_id: int):
            conn = Database.get_connection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            sql = "SELECT * FROM semi_vendings WHERE guild_id = ?"
            cur.execute(sql, (guild_id,))

            results = cur.fetchall()
            if not results:
                return None

            return [Database.SemiVending(
                i["id"],
                i["guild_id"],
                i["name"],
                i["link_channel_id"],
                i["performance_channel_id"],
                i["buyer_role"],
                datetime.strptime(i["created_at"], "%Y-%m-%d %H:%M:%S"),
            ) for i in results]

    class SemiVendingProduct:
        def __init__(self, vending_id: int, product_id: int, name: str, description: str,
                     price: int, created_at: datetime):
            self.vending_id = vending_id
            self.product_id = product_id
            self.name = name
            self.description = description
            self.price = price
            self.created_at = created_at

        def edit_name(self, name: str):
            conn = Database.get_connection()
            cur = conn.cursor()

            sql = "UPDATE semi_vending_products SET name = ? WHERE product_id = ?"
            cur.execute(sql, (name, self.product_id,))

            conn.commit()
            conn.close()

        def edit_description(self, description: str):
            conn = Database.get_connection()
            cur = conn.cursor()

            sql = "UPDATE semi_vending_products SET description = ? WHERE product_id = ?"
            cur.execute(sql, (description, self.product_id,))

            conn.commit()
            conn.close()

        def edit_price(self, price: int):
            conn = Database.get_connection()
            cur = conn.cursor()

            sql = "UPDATE semi_vending_products SET price = ? WHERE product_id = ?"
            cur.execute(sql, (price, self.product_id,))

            conn.commit()
            conn.close()

        def delete(self):
            conn = Database.get_connection()
            cur = conn.cursor()

            sql = "DELETE FROM semi_vending_products WHERE product_id = ?"
            cur.execute(sql, (self.product_id,))

            conn.commit()
            conn.close()

        def return_order_by_latest(self, number_stocks: int):
            conn = Database.get_connection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            sql = "SELECT * FROM semi_vending_stocks WHERE product_id = ? AND status = 1 ORDER BY stock_id DESC LIMIT ?"
            cur.execute(sql, (self.product_id, number_stocks))

            results = cur.fetchall()
            if not results or len(results) < number_stocks:
                return None

            stocks = [Database.SemiVendingStock(
                i["value"],
                i["product_id"],
                i["stock_id"],
                datetime.strptime(i["created_at"], "%Y-%m-%d %H:%M:%S"),
            ) for i in results]

            for i in stocks:
                cur.execute("DELETE FROM semi_vending_stocks WHERE stock_id = ?", (i.stock_id,))

            conn.commit()
            conn.close()

            return stocks

        def return_order_by_oldest(self, number_stocks: int):
            conn = Database.get_connection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            sql = "SELECT * FROM semi_vending_stocks WHERE product_id = ? AND status = 1 ORDER BY stock_id ASC LIMIT ?"
            cur.execute(sql, (self.product_id, number_stocks))

            results = cur.fetchall()
            if not results or len(results) < number_stocks:
                return None

            stocks = [Database.SemiVendingStock(
                i["value"],
                i["product_id"],
                i["stock_id"],
                datetime.strptime(i["created_at"], "%Y-%m-%d %H:%M:%S"),
            ) for i in results]

            for i in stocks:
                cur.execute("DELETE FROM semi_vending_stocks WHERE stock_id = ?", (i.stock_id,))

            conn.commit()
            conn.close()

            return stocks

        def return_all(self):
            conn = Database.get_connection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            sql = "SELECT * FROM semi_vending_stocks WHERE product_id = ? AND status = 1 ORDER BY stock_id ASC"
            cur.execute(sql, (self.product_id,))

            results = cur.fetchall()
            if not results:
                return []

            stocks = [Database.SemiVendingStock(
                i["value"],
                i["product_id"],
                i["stock_id"],
                datetime.strptime(i["created_at"], "%Y-%m-%d %H:%M:%S"),
            ) for i in results]

            for i in stocks:
                cur.execute("DELETE FROM semi_vending_stocks WHERE stock_id = ?", (i.stock_id,))

            conn.commit()
            conn.close()

            return stocks

        def buy(self, quantity: int):
            stocks = Database.SemiVendingStock.get(self.product_id)[:quantity]
            for i in stocks:
                i.to_reservation()

            return stocks

        @property
        def stocks(self):
            return Database.SemiVendingStock.get(self.product_id)

        @staticmethod
        def get(vending_id: int):
            conn = Database.get_connection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            sql = "SELECT * FROM semi_vending_products WHERE vending_id = ?"
            cur.execute(sql, (vending_id,))

            results = cur.fetchall()
            if not results:
                return []

            return [Database.SemiVendingProduct(
                vending_id,
                i["product_id"],
                i["name"],
                i["description"],
                i["price"],
                datetime.strptime(i["created_at"], "%Y-%m-%d %H:%M:%S"),
            ) for i in results]

        @staticmethod
        def add(vending_id: int, name: str, description: str, price: int):
            conn = Database.get_connection()
            cur = conn.cursor()

            now = datetime.now().replace(microsecond=0)
            sql = "INSERT INTO semi_vending_products(vending_id, name, description, price, created_at) VALUES(?, ?, ?, ?, ?)"
            cur.execute(sql, (vending_id, name, description, price, str(now)))

            conn.commit()
            conn.close()

    class SemiVendingStock:
        def __init__(self, value: str, product_id: int, stock_id: int, created_at: datetime):
            self.value = value
            self.product_id = product_id
            self.stock_id = stock_id
            self.created_at = created_at

        def to_reservation(self):
            conn = Database.get_connection()
            cur = conn.cursor()

            sql = "UPDATE semi_vending_stocks SET status = -1 WHERE stock_id = ?"
            cur.execute(sql, (self.stock_id,))

            conn.commit()
            conn.close()

        @staticmethod
        def get(product_id: int):
            conn = Database.get_connection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            sql = "SELECT * FROM semi_vending_stocks WHERE product_id = ? AND status = 1 ORDER BY stock_id ASC"
            cur.execute(sql, (product_id,))

            results = cur.fetchall()
            if not results:
                return []

            return [Database.SemiVendingStock(
                i["value"],
                i["product_id"],
                i["stock_id"],
                datetime.strptime(i["created_at"], "%Y-%m-%d %H:%M:%S"),
            ) for i in results]

        @staticmethod
        def add(product_id: int, value: str):
            conn = Database.get_connection()
            cur = conn.cursor()

            now = datetime.now().replace(microsecond=0)
            sql = "INSERT INTO semi_vending_stocks(product_id, value, status, created_at) VALUES(?, ?, 1, ?)"
            cur.execute(sql, (product_id, value, str(now)))

            conn.commit()
            conn.close()

    class SemiVendingOrder:
        def __init__(self, order_id: int, user_id: int, vending_id: int, product_id: int, stock_id: list[int], total: int, created_at: datetime):
            self.order_id = order_id
            self.user_id = user_id
            self.vending_id = vending_id
            self.product_id = product_id
            self.stock_id = stock_id
            self.total = total
            self.created_at = created_at

        @staticmethod
        def get(order_id: int):
            conn = Database.get_connection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            sql = "SELECT * FROM semi_vending_stocks WHERE order_id = ?"
            cur.execute(sql, (order_id,))

            result = cur.fetchone()
            if not result:
                return []

            return Database.SemiVendingOrder(
                result["order_id"],
                result["user_id"],
                result["vending_id"],
                result["product_id"],
                result["stock_id"],
                json.loads(result["total"]),
                datetime.strptime(result["created_at"], "%Y-%m-%d %H:%M:%S")
            )

        @staticmethod
        def add(user_id: int, vending_id: int, product_id: int, stock_id: list[int], total: int):
            conn = Database.get_connection()
            cur = conn.cursor()

            while True:
                order_id = secrets.randbelow(999999999)
                try:
                    now = datetime.now().replace(microsecond=0)
                    sql = "INSERT INTO semi_vending_orders VALUES(?, ?, ?, ?, ?, ?, ?)"
                    cur.execute(sql, (order_id, user_id, vending_id, product_id, json.dumps(stock_id), total, str(now)))

                    return Database.SemiVendingOrder(
                        order_id,
                        user_id,
                        vending_id,
                        product_id,
                        stock_id,
                        total,
                        now,
                    )

                except sqlite3.IntegrityError as e:
                    if e.args[0].startswith('UNIQUE constraint failed:'):
                        continue

                    traceback.print_exc()
                    break

            conn.commit()
            conn.close()


