"""
添加测试数据脚本
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Product, Review

# 中文书名图片
book_images = [
    'static/images/数据结构与算法.jpg',
    'static/images/机器学习基础.jpg',
    'static/images/深度学习导论及案例分析.jpg',
    'static/images/python编程从入门到实战.jpg',
    'static/images/python编程从入门到精通.jpg',
    'static/images/高等数学上.jpg',
    'static/images/高等数学第八版.png',
    'static/images/软件工程.jpg',
    'static/images/管理学.png',
    'static/images/机器学习基础及应用.jpg',
    'static/images/深度学习基础及应用.jpg',
]

# 书籍数据
books_data = [
    {'name': '数据结构与算法', 'description': '经典的算法教材，详细讲解各种数据结构和算法设计', 'price': 50.00, 'degree_of_wear': '九五成新'},
    {'name': '机器学习基础', 'description': '机器学习入门教材，涵盖监督学习、无监督学习等核心内容', 'price': 45.00, 'degree_of_wear': '九成新'},
    {'name': '深度学习导论及案例分析', 'description': '深度学习入门教程，包含神经网络、卷积网络等基础知识', 'price': 55.00, 'degree_of_wear': '九成新'},
    {'name': 'Python编程从入门到实战', 'description': '全面介绍Python编程基础，包含项目实战案例', 'price': 35.50, 'degree_of_wear': '八成新'},
    {'name': '高等数学（上）', 'description': '高等数学上册，涵盖极限、导数、积分等内容', 'price': 30.00, 'degree_of_wear': '八五成新'},
    {'name': '软件工程', 'description': '软件工程导论，讲解软件开发流程和方法论', 'price': 42.00, 'degree_of_wear': '九成新'},
    {'name': '管理学原理', 'description': '管理学基础教材，涵盖管理职能和组织理论', 'price': 38.00, 'degree_of_wear': '八成新'},
    {'name': '机器学习基础及应用', 'description': '机器学习算法实践指南，包含scikit-learn使用案例', 'price': 48.00, 'degree_of_wear': '九五成新'},
]

def add_test_users():
    """添加测试用户"""
    with app.app_context():
        # 用户1：卖家
        user1 = User(
            email='seller@test.com',
            phone='13800138001',
            credit_score=95.0,
            credit_level='A',
            total_trades=15,
            positive_rates=98.0
        )
        user1.set_password('123456')
        db.session.add(user1)
        
        # 用户2：买家
        user2 = User(
            email='buyer@test.com',
            phone='13900139002',
            credit_score=88.0,
            credit_level='B',
            total_trades=8,
            positive_rates=100.0
        )
        user2.set_password('123456')
        db.session.add(user2)
        
        # 用户3：普通用户
        user3 = User(
            email='user@test.com',
            phone='13700137003',
            credit_score=72.0,
            credit_level='B',
            total_trades=5,
            positive_rates=90.0
        )
        user3.set_password('123456')
        db.session.add(user3)
        
        db.session.commit()
        print("[OK] 添加3个测试用户")
        return [user1.id, user2.id, user3.id]

def add_test_products(user_ids):
    """为用户添加测试商品"""
    with app.app_context():
        seller_id = user_ids[0]
        buyer_id = user_ids[1]
        
        # 卖家上传的书籍
        for i, book in enumerate(books_data[:6]):
            product = Product(
                name=book['name'],
                description=book['description'],
                price=book['price'],
                degree_of_wear=book['degree_of_wear'],
                image=book_images[i],
                user_id=seller_id
            )
            db.session.add(product)
        
        # 买家上传的书籍
        for i, book in enumerate(books_data[6:8]):
            product = Product(
                name=book['name'],
                description=book['description'],
                price=book['price'],
                degree_of_wear=book['degree_of_wear'],
                image=book_images[i+6],
                user_id=buyer_id
            )
            db.session.add(product)
        
        db.session.commit()
        print("[OK] 添加8个测试商品")

def add_test_reviews(user_ids):
    """添加测试评价"""
    with app.app_context():
        seller_id = user_ids[0]
        buyer_id = user_ids[1]
        user3_id = user_ids[2]
        
        # 获取卖家的商品
        seller_products = Product.query.filter_by(user_id=seller_id).all()
        
        if seller_products:
            # 买家对卖家的评价
            review1 = Review(
                order_id=1,
                reviewer_id=buyer_id,
                reviewee_id=seller_id,
                rating=5,
                comment='卖家服务态度很好，书籍质量也很棒，下次还会购买！',
                is_anonymous=False
            )
            db.session.add(review1)
            
            # 用户3对卖家的评价
            review2 = Review(
                order_id=2,
                reviewer_id=user3_id,
                reviewee_id=seller_id,
                rating=4,
                comment='书籍包装很仔细，发货速度快，好评！',
                is_anonymous=True
            )
            db.session.add(review2)
            
            # 另一个评价
            review3 = Review(
                order_id=3,
                reviewer_id=buyer_id,
                reviewee_id=seller_id,
                rating=5,
                comment='非常满意的一次交易！',
                is_anonymous=False
            )
            db.session.add(review3)
            
            db.session.commit()
            print("[OK] 添加3条测试评价")

def main():
    print("正在添加测试数据...")
    
    # 添加用户
    user_ids = add_test_users()
    
    # 添加商品
    add_test_products(user_ids)
    
    # 添加评价
    add_test_reviews(user_ids)
    
    print("\n[OK] 测试数据添加完成！")
    print(f"\n测试用户：")
    print(f"  卖家: seller@test.com / 123456")
    print(f"  买家: buyer@test.com / 123456")
    print(f"  用户3: user@test.com / 123456")
    
    print(f"\n信用主页地址：")
    print(f"  卖家信用: http://127.0.0.1:5003/credit/{user_ids[0]}")
    print(f"  买家信用: http://127.0.0.1:5003/credit/{user_ids[1]}")
    
    print(f"\n评价页面地址：")
    print(f"  卖家评价: http://127.0.0.1:5003/reviews/{user_ids[0]}")

if __name__ == '__main__':
    main()