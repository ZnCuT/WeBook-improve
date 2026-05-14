import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Product, Review

# 更多书籍数据
more_books = [
    {'name': '高等数学第八版', 'description': '同济大学高等数学第八版，经典教材', 'price': 45.00, 'degree_of_wear': '九成新', 'image': 'static/images/高等数学第八版.png'},
    {'name': '管理学', 'description': '管理学原理与实践，适合经管类学生', 'price': 36.00, 'degree_of_wear': '八成新', 'image': 'static/images/管理学.png'},
    {'name': '深度学习基础及应用', 'description': '深度学习实战指南，包含TensorFlow和PyTorch示例', 'price': 58.00, 'degree_of_wear': '九五成新', 'image': 'static/images/深度学习基础及应用.jpg'},
    {'name': '高等数学第三版', 'description': '高等数学第三版，基础教材', 'price': 32.00, 'degree_of_wear': '八成新', 'image': 'static/images/高等数学第三版.png'},
]

def add_products():
    with app.app_context():
        seller_id = 1
        buyer_id = 2
        
        # 给卖家添加更多商品
        for book in more_books[:2]:
            product = Product(
                name=book['name'],
                description=book['description'],
                price=book['price'],
                degree_of_wear=book['degree_of_wear'],
                image=book['image'],
                user_id=seller_id
            )
            db.session.add(product)
        
        # 给买家添加商品
        for book in more_books[2:]:
            product = Product(
                name=book['name'],
                description=book['description'],
                price=book['price'],
                degree_of_wear=book['degree_of_wear'],
                image=book['image'],
                user_id=buyer_id
            )
            db.session.add(product)
        
        db.session.commit()
        print("Added 4 more products")

def add_reviews():
    with app.app_context():
        # 添加评价：买家评价卖家
        review1 = Review(
            order_id=1,
            reviewer_id=2,  # buyer
            reviewee_id=1,  # seller
            rating=5,
            comment='非常好的卖家，书籍包装精美，发货速度快！',
            is_anonymous=False
        )
        
        review2 = Review(
            order_id=2,
            reviewer_id=3,  # user3
            reviewee_id=1,  # seller
            rating=4,
            comment='书籍质量不错，卖家沟通很耐心',
            is_anonymous=True
        )
        
        review3 = Review(
            order_id=3,
            reviewer_id=2,  # buyer
            reviewee_id=1,  # seller
            rating=5,
            comment='第二次购买了，一如既往的好！',
            is_anonymous=False
        )
        
        # 添加评价：用户3评价买家
        review4 = Review(
            order_id=4,
            reviewer_id=1,  # seller
            reviewee_id=2,  # buyer
            rating=5,
            comment='买家很爽快，交易顺利！',
            is_anonymous=False
        )
        
        db.session.add_all([review1, review2, review3, review4])
        db.session.commit()
        print("Added 4 reviews")

if __name__ == '__main__':
    add_products()
    add_reviews()
    print("Done!")