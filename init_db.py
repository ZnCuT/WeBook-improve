"""
数据库初始化和索引管理脚本
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Product, semantic_service, init_semantic_service


def init_database():
    """初始化数据库表"""
    with app.app_context():
        print("正在创建数据库表...")
        db.create_all()
        print("数据库表创建成功!")
        
        # 检查是否有数据
        product_count = Product.query.count()
        print(f"当前商品数量: {product_count}")


def rebuild_semantic_index():
    """重建语义检索索引"""
    with app.app_context():
        print("正在初始化语义检索服务...")
        init_semantic_service()
        
        print("正在获取所有商品...")
        products = Product.query.all()
        print(f"找到 {len(products)} 个商品")
        
        if products:
            print("正在重建语义检索索引...")
            semantic_service.rebuild_index(products)
            print("索引重建完成!")
        else:
            print("没有商品数据,跳过索引创建")


def add_sample_data():
    """添加示例数据"""
    with app.app_context():
        # 检查是否已有数据
        if Product.query.count() > 0:
            print("数据库已有数据,跳过示例数据添加")
            return
        
        print("正在添加示例数据...")
        
        sample_products = [
            {
                'name': '深度学习入门',
                'description': '适合初学者的深度学习教程,包含神经网络、卷积网络等基础知识',
                'price': 45.00,
                'degree_of_wear': '九成新',
                'image': 'uploads/images/book1.png'
            },
            {
                'name': 'Python编程从入门到实践',
                'description': '全面介绍Python编程基础,包含项目实战案例',
                'price': 35.50,
                'degree_of_wear': '八成新',
                'image': 'uploads/images/book2.png'
            },
            {
                'name': '数据结构与算法分析',
                'description': '经典的算法教材,详细讲解各种数据结构和算法设计',
                'price': 50.00,
                'degree_of_wear': '九五成新',
                'image': 'uploads/images/数据结构与算法.jpg'
            },
            {
                'name': '机器学习实战',
                'description': '机器学习算法的实践指南,包含scikit-learn使用案例',
                'price': 42.00,
                'degree_of_wear': '九成新',
                'image': 'uploads/images/book3.png'
            },
            {
                'name': 'Web开发完全指南',
                'description': 'HTML、CSS、JavaScript全栈开发教程',
                'price': 38.00,
                'degree_of_wear': '八五成新',
                'image': 'uploads/images/book1.png'
            }
        ]
        
        for data in sample_products:
            product = Product(**data)
            db.session.add(product)
        
        db.session.commit()
        print(f"成功添加 {len(sample_products)} 个示例商品")


def show_menu():
    """显示菜单"""
    print("\n" + "="*50)
    print("WeBook 数据库管理工具")
    print("="*50)
    print("1. 初始化数据库表")
    print("2. 添加示例数据")
    print("3. 重建语义检索索引")
    print("4. 全部执行 (初始化+示例数据+索引)")
    print("0. 退出")
    print("="*50)


if __name__ == '__main__':
    while True:
        show_menu()
        choice = input("\n请选择操作 (0-4): ").strip()
        
        if choice == '1':
            init_database()
        elif choice == '2':
            add_sample_data()
        elif choice == '3':
            rebuild_semantic_index()
        elif choice == '4':
            print("\n开始执行完整初始化流程...")
            init_database()
            add_sample_data()
            rebuild_semantic_index()
            print("\n✓ 所有操作完成!")
        elif choice == '0':
            print("退出程序")
            break
        else:
            print("无效的选择,请重试")
