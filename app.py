from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash, jsonify, Response, send_file
from config import Config
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from simple_semantic import get_simple_search
from knowledge_base import knowledge_base
from sparql_search import semantic_search_service
import base64, io
from uuid import uuid4
app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

# 初始化简单语义搜索服务
simple_search = get_simple_search()

# 将数据库表创建放在模型定义之后

def sync_database_to_knowledge_base():
    """同步数据库数据到语义知识库"""
    try:
        products = Product.query.all()
        for product in products:
            book_data = {
                'id': product.id,
                'name': product.name,
                'description': product.description or '',
                'price': float(product.price),
                'degree_of_wear': product.degree_of_wear or 'unknown'
            }
            knowledge_base.add_book_to_kb(book_data)
        
        print(f"[OK] 已同步 {len(products)} 本书籍到语义知识库")
        return True
        
    except Exception as e:
        print(f"[ERROR] 同步数据到知识库时出错: {e}")
        return False

def convert_sparql_results_to_products(sparql_results):
    """将SPARQL搜索结果转换为Product对象"""
    products = []
    for result in sparql_results:
        try:
            product_id = int(result['id'])
            product = Product.query.get(product_id)
            if product:
                products.append(product)
        except (ValueError, TypeError):
            # 如果ID无效，跳过这个结果
            continue
    
    return products

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    degree_of_wear = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(200), nullable=False)  # 存储文件路径
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    seller_contact = db.Column(db.String(200))  # 卖家联系方式
    is_sold = db.Column(db.Boolean, default=False)  # 是否已售出
    buyer_id = db.Column(db.Integer)  # 购买者ID
    user_id = db.Column(db.Integer)  # 上传者ID

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # 去掉unique约束
    phone = db.Column(db.String(20))  # 用户联系电话

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(80), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    product_image = db.Column(db.String(200))
    seller_contact = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, paid, completed
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# 在应用上下文中创建数据库表（必须在模型定义之后）
with app.app_context():
    db.create_all()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method in ['GET', 'POST']:
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('login_success'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/get')
def get_session():
    return session.get('user_id')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('register'))
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/homepage')
def homepage():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    uploaded_products = Product.query.filter_by(user_id=user_id).all()
    sold_products = Product.query.filter_by(user_id=user_id, is_sold=True).all()
    orders = Order.query.filter_by(user_id=user_id).all()
    return render_template('homepage.html', uploaded_products=uploaded_products, sold_products=sold_products, orders=orders)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        name = request.form.get('name')
        price_str = request.form.get('price')
        if not price_str:
            flash('Please enter the price')
            return "Price is required"
        price = float(price_str)
        description = request.form.get('description')
        degree_of_wear = request.form.get('degree_of_wear')
        seller_contact = request.form.get('seller_contact', '')
        image = request.files['image']

        image_rel = None
        if image and allowed_file(image.filename):
            # 生成唯一文件名，避免覆盖
            original = secure_filename(image.filename)
            unique_name = f"{uuid4().hex}_{original}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            image.save(save_path)
            # 在数据库中仅存相对static的路径，使用正斜杠，便于通过url_for('static', filename=...)
            image_rel = f"uploads/{unique_name}"

        new_product = Product(name=name, price=price, description=description, degree_of_wear=degree_of_wear, image=image_rel or '', seller_contact=seller_contact, user_id=session.get('user_id'))
        db.session.add(new_product)
        db.session.commit()
        
        # 添加到语义检索索引（简单版本无需额外操作）
        # simple_search 直接搜索数据库，无需维护索引
        
        flash('Book uploaded successfully!')
        return redirect(url_for('homepage'))
    return render_template("upload.html")


@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    query = ''
    search_mode = 'keyword'  # 默认关键词搜索
    
    if request.method == 'POST':
        query = request.form.get('query')
        search_mode = request.form.get('search_mode', 'keyword')
        
        if not query:
            flash('请输入搜索关键词')
            return redirect(url_for('search'))
        
        if search_mode == 'sparql':
            # SPARQL语义知识图谱搜索
            sync_database_to_knowledge_base()  # 同步数据到知识库
            sparql_results = semantic_search_service.semantic_search(query, limit=20)
            results = convert_sparql_results_to_products(sparql_results)
            
        elif search_mode == 'semantic':
            # 简单语义搜索
            all_products = Product.query.all()
            search_results = simple_search.search(query, all_products, top_k=20)
            if search_results:
                product_ids = [pid for pid, score in search_results]
                results = Product.query.filter(Product.id.in_(product_ids)).all()
                # 按相似度排序
                results = sorted(results, key=lambda p: next((score for pid, score in search_results if pid == p.id), 0), reverse=True)
        else:
            # 关键词搜索（默认）
            results = Product.query.filter(Product.name.ilike(f"%{query}%") | Product.description.ilike(f"%{query}%")).all()
    
    return render_template('search.html', results=results, query=query, search_mode=search_mode)

@app.route('/products/<int:id>')
def book_detail(id):
    from datetime import datetime
    product = Product.query.get(id)
    if product is None:
        return "Product not found", 404
    current_time = datetime.now().strftime('%Y%m%d%H%M%S')
    return render_template('book_detail.html', product=product, current_time=current_time)

@app.route('/image/<int:product_id>')
def get_image(product_id):
    # 兼容历史：若数据库保存了相对路径（推荐），则转为通过static服务；
    # 若未来保存为base64，可在此分支处理，但当前实现仅支持路径方式。
    product = Product.query.get(product_id)
    if not product or not product.image:
        return "No image available", 404

    rel_path = product.image.replace('\\', '/')
    # 移除可能存在的前缀"static/"
    if rel_path.startswith('static/'):
        rel_path = rel_path[len('static/'):]

    # 通过静态目录发送文件
    return send_from_directory('static', rel_path)
  
@app.route('/check_data')
def check_data():
    products = Product.query.all()  
    return render_template('check_data.html', products=products)
   
@app.route('/buy/<int:id>', methods=['POST', 'GET'])
def book_details(id):
    product = Product.query.get(id)
    if product is None:
        return "Product not found", 404
    db.session.delete(product)
    db.session.commit()
    
    # 简单版本无需索引维护
    
    return "delete successfully!"

@app.route('/login_success')
def login_success():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('login_success.html')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"message": "Product not found"}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': product.id,
        'description': product.description,
        'price': product.price,
        'degree_of_wear': product.degree_of_wear,
        'image': product.image,
        'name': product.name,
        'seller_contact': product.seller_contact
    } for product in products])

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"message": "Product not found"}), 404
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'description': product.description,
        'degree_of_wear': product.degree_of_wear,
        'image': product.image,
        'seller_contact': product.seller_contact
    })

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"message": "Product not found"}), 404
    
    data = request.get_json()
    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'description' in data:
        product.description = data['description']
    if 'degree_of_wear' in data:
        product.degree_of_wear = data['degree_of_wear']
    if 'seller_contact' in data:
        product.seller_contact = data['seller_contact']
    
    db.session.commit()
    return jsonify({"message": "Product updated successfully"})

@app.route('/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if order is None:
        return jsonify({"message": "Order not found"}), 404
    return jsonify({
        'id': order.id,
        'product_name': order.product_name,
        'product_price': order.product_price,
        'product_image': order.product_image,
        'seller_contact': order.seller_contact,
        'status': order.status
    })

@app.route('/create_order', methods=['POST'])
def create_order():
    data = request.get_json()
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"success": False, "message": "User not logged in"}), 401
    
    # 获取商品
    product = Product.query.get(data.get('product_id'))
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404
    
    # 检查商品是否已售出
    if product.is_sold:
        return jsonify({"success": False, "message": "Product has been sold"}), 400
    
    new_order = Order(
        user_id=user_id,
        product_id=data.get('product_id'),
        product_name=data.get('product_name'),
        product_price=data.get('product_price'),
        product_image=data.get('product_image', ''),
        seller_contact=data.get('seller_contact', ''),
        status='paid'
    )
    
    db.session.add(new_order)
    
    # 更新商品状态为已售出，并记录购买者ID
    product.is_sold = True
    product.buyer_id = user_id
    
    db.session.commit()
    
    return jsonify({"success": True, "order_id": new_order.id})


@app.route('/api/rebuild_index', methods=['POST'])
def rebuild_index():
    """重建索引（简单版本无需操作）"""
    try:
        products = Product.query.all()
        return jsonify({
            "message": "简单版本无需重建索引",
            "total_products": len(products)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/semantic_search', methods=['POST'])
def api_semantic_search():
    """简单语义搜索API"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 10)
        
        if not query:
            return jsonify({"error": "The query cannot be empty"}), 400
        
        # 执行简单语义搜索
        all_products = Product.query.all()
        search_results = simple_search.search(query, all_products, top_k=top_k)
        
        if not search_results:
            return jsonify({"results": []}), 200
        
        # 获取商品详情
        product_ids = [pid for pid, score in search_results]
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        
        # 构建结果
        results = []
        for product in products:
            score = next((s for pid, s in search_results if pid == product.id), 0)
            results.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'degree_of_wear': product.degree_of_wear,
                'image_url': product.image,
                'similarity_score': score
            })
        
        # 按相似度排序
        results = sorted(results, key=lambda x: x['similarity_score'], reverse=True)
        
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 知识库管理路由
@app.route('/kb/sync')
def sync_kb():
    """手动同步知识库"""
    if sync_database_to_knowledge_base():
        flash('✅ 知识库同步完成')
    else:
        flash('❌ 知识库同步失败')
    return redirect(url_for('search'))

@app.route('/kb/stats')
def kb_stats():
    """显示知识库统计信息"""
    try:
        stats = knowledge_base.get_stats()
        return render_template('kb_stats.html', stats=stats)
    except Exception as e:
        flash(f'获取知识库统计信息失败: {e}')
        return redirect(url_for('search'))

@app.route('/api/search_suggestions')
def search_suggestions():
    """搜索建议API"""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    try:
        suggestions = semantic_search_service.get_search_suggestions(query)
        return jsonify(suggestions)
    except Exception as e:
        print(f"获取搜索建议失败: {e}")
        return jsonify([])

@app.route('/api/book_recommendations/<int:book_id>')
def book_recommendations(book_id):
    """书籍推荐API"""
    try:
        recommendations = semantic_search_service.get_recommendations_by_book_id(str(book_id))
        return jsonify(recommendations)
    except Exception as e:
        print(f"获取推荐失败: {e}")
        return jsonify([])

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    print("[INFO] WeBook应用正在启动...")
    print(f"[INFO] 数据库类型: {'SQLite' if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite') else 'MySQL'}")
    print(f"[INFO] 数据库URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print(f"[INFO] 上传文件夹: {app.config['UPLOAD_FOLDER']}")
    print(f"[INFO] 语义知识库: 已集成SPARQL搜索")
    print("[INFO] 访问地址: http://127.0.0.1:5003")
    app.run(debug=True, port=5003)
