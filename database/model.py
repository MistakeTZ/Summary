import sqlite3
from sqlite3 import Connection, Cursor
from os import path

connection: Connection
cur: Cursor


class DB():
    
    def load_database(dbname = "db.sqlite3"):
        global connection, cur

        try:
            dbname = path.join("database", dbname)
            connection = sqlite3.connect(dbname)
            cur = connection.cursor()

            print("Database connected")
        except:
            raise ValueError("Connection to database failed")


    def create_tables():
        cur.execute("""create table if not exists users (
                         id integer primary key autoincrement,
                         telegram_id bigint not null,
                         name text not null,
                         registered timestamp
                         )""")
        
        cur.execute("""create table if not exists payments (
                         id integer primary key autoincrement,
                         telegram_id bigint not null,
                         have_tz bool default false,
                         product varchar(255),
                         payment_id varchar(25),
                         payment_amount int,
                         payment_confirmed bool default false,
                         payment_date timestamp,
                         provider_payment_charge_id varchar(100),
                         telegram_payment_charge_id varchar(100),
                         registered timestamp
                         )""")
        connection.commit()


    def select(by_value, field="telegram_id", table="users"):
        return DB.get("select * from {} where {} = ?".format(table, field), [by_value], True)
    

    def get(prompt, values=[], one=False):
        try:
            cur.execute(prompt, values)
            if one:
                return cur.fetchone()
            else:
                return cur.fetchall()
        except Exception as e:
            print(e)
            return False
        

    def get_dict(prompt, values=[], one=False):
        try:
            cur.execute(prompt, values)
            desc = [row[0] for row in cur.description]
            if one:
                return dict(zip(desc, cur.fetchone()))
            else:
                return [dict(zip(desc, res)) for res in cur.fetchall()]
        except Exception as e:
            print(e)
            return False
        

    def commit(prompt, values=[]):
        try:
            cur.execute(prompt, values)
            connection.commit()
            return True
        except Exception as e:
            print(e)
            return False


    def unload_database():
        connection.close()
