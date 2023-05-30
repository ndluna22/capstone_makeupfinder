"""Seed database with sample data from CSV Files."""
from app import db
from models import db

# import json
# import urllib3
# import psycopg2


db.drop_all()
db.create_all()


############

# Add API TO SQL DATABASE

# conn = psycopg2.connect(database="makeup")
# cur = conn.cursor()

# http = urllib3.PoolManager()
# url = "http://makeup-api.herokuapp.com/api/v1/products.json"

# try:
#     response = http.request('GET', url)
#     data = json.loads(response.data.decode('utf-8'))
#     index = 0  # I'm using index as an id_key

#     for i in data:
#         no = None
#         product_id = None
#         name = None
#         brand = None

#         no = i['id']
#         product_id = i['id']
#         name = i['name']
#         brand = i['brand']

#         cur.execute("""
#             INSERT INTO products
#             VALUES (%s, %s, %s,%s);
#             """,
#                     (product_id, name, brand))
#         conn.commit()
#         index += 1
#     cur.close()
# except psycopg2.Error as e:
#     error = e.pgcode

###
