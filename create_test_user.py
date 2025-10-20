#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建测试用户的脚本
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        print("正在导入模块...")
        from app import app, db, User
        print("模块导入成功")
        
        with app.app_context():
            print("创建数据库表...")
            db.create_all()
            
            email = 'admin@webook.com'
            password = 'admin123'
            
            print(f"检查用户 {email} 是否存在...")
            existing = User.query.filter_by(email=email).first()
            
            if existing:
                print(f"用户 {email} 已存在 (ID: {existing.id})")
                # 验证密码
                if existing.check_password(password):
                    print("✅ 现有用户密码验证成功")
                else:
                    print("❌ 现有用户密码不匹配，更新密码...")
                    existing.set_password(password)
                    db.session.commit()
                    print("✅ 密码已更新")
            else:
                print("创建新用户...")
                user = User(email=email)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                print(f"✅ 成功创建用户: {email}")
            
            print(f"\n🎉 登录信息:")
            print(f"📧 邮箱: {email}")
            print(f"🔑 密码: {password}")
            print(f"🌐 网站: http://127.0.0.1:5003")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    if success:
        print("\n✅ 用户创建完成！现在可以使用上述账号登录网站了。")
    else:
        print("\n❌ 用户创建失败，请检查错误信息。")