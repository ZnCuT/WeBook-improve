import sqlite3
import os

from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret_key'
bcrypt = Bcrypt(app)

db_path = 'instance/webook.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS users")
    print("已删除旧表")
except:
    pass

cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    phone VARCHAR(20)
)
''')

cursor.execute('''
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    price FLOAT NOT NULL,
    description VARCHAR(200) NOT NULL,
    degree_of_wear VARCHAR(80) NOT NULL,
    image VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    seller_contact VARCHAR(200),
    is_sold INTEGER DEFAULT 0,
    buyer_id INTEGER,
    user_id INTEGER
)
''')

cursor.execute('''
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(80) NOT NULL,
    product_price FLOAT NOT NULL,
    product_image VARCHAR(200),
    seller_contact VARCHAR(200),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

users = [
    ('user1@example.com', bcrypt.generate_password_hash('password123').decode('utf-8'), '1234567890'),
    ('user2@example.com', bcrypt.generate_password_hash('password123').decode('utf-8'), '0987654321'),
]

cursor.executemany('INSERT INTO users (email, password, phone) VALUES (?, ?, ?)', users)

books = [
    ('python编程从入门到实战', 29.99, 'Python编程入门书籍', '九成新', 'images/python编程从入门到实战.jpg', 'user1@example.com', 1),
    ('python编程从入门到精通', 35.99, 'Python进阶书籍', '八成新', 'images/python编程从入门到精通.jpg', 'user1@example.com', 1),
    ('数据结构与算法', 28.99, '计算机基础课程', '九成新', 'images/数据结构与算法.jpg', 'user1@example.com', 1),
    ('机器学习基础', 45.99, '机器学习入门经典', '九五新', 'images/机器学习基础.jpg', 'user1@example.com', 1),
    ('机器学习基础及应用', 52.99, '机器学习理论与实践', '八成新', 'images/机器学习基础及应用.jpg', 'user1@example.com', 1),
    ('深度学习基础及应用', 48.99, '深度学习入门书籍', '九成新', 'images/深度学习基础及应用.jpg', 'user2@example.com', 2),
    ('深度学习导论及案例分析', 55.99, '深度学习进阶书籍', '九五新', 'images/深度学习导论及案例分析.jpg', 'user2@example.com', 2),
    ('管理学', 22.99, '管理学基础理论', '七成新', 'images/管理学.png', 'user2@example.com', 2),
    ('软件工程', 25.99, '软件工程导论', '八成新', 'images/软件工程.jpg', 'user2@example.com', 2),
    ('高等数学上', 18.99, '大学高等数学教材', '六成新', 'images/高等数学上.jpg', 'user2@example.com', 2),
    ('高等数学第三版', 20.99, '高等数学教材第三版', '七成新', 'images/高等数学第三版.png', 'user2@example.com', 2),
    ('高等数学第八版', 24.99, '高等数学教材第八版', '八成新', 'images/高等数学第八版.png', 'user2@example.com', 2),
]

cursor.executemany('''
INSERT INTO products (name, price, description, degree_of_wear, image, seller_contact, user_id)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', books)

conn.commit()
conn.close()

print("数据库已重新创建！")
print("=" * 50)
print("测试账号:")
print("  账号1: user1@example.com / password123")
print("  账号2: user2@example.com / password123")
print("=" * 50)
print("账号1的书籍: python编程从入门到实战、python编程从入门到精通、数据结构与算法、机器学习基础、机器学习基础及应用")
print("账号2的书籍: 深度学习基础及应用、深度学习导论及案例分析、管理学、软件工程、高等数学上、高等数学第三版、高等数学第八版")
