import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Product, Review

with app.app_context():
    print("=== Database Statistics ===")
    print(f"Users: {User.query.count()}")
    print(f"Products: {Product.query.count()}")
    print(f"Reviews: {Review.query.count()}")
    
    print("\n=== User List ===")
    for u in User.query.all():
        print(f"ID:{u.id} | {u.email} | Credit:{u.credit_score}({u.credit_level})")
    
    print("\n=== Product List ===")
    for p in Product.query.all():
        print(f"ID:{p.id} | {p.name} | Price:{p.price} | Seller:{p.user_id}")
    
    print("\n=== Review List ===")
    for r in Review.query.all():
        print(f"ID:{r.id} | Rating:{r.rating} | From:{r.reviewer_id} -> To:{r.reviewee_id}")