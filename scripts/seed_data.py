"""
Database seeder script for creating admin user and sample data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.core.security import get_password_hash
from app.config import settings


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def seed_admin_user(db):
    """Seed admin user"""
    print("Seeding admin user...")
    
    # Check if admin exists
    admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    
    if admin:
        print("✓ Admin user already exists")
        return admin
    
    # Create admin user
    admin = User(
        email=settings.ADMIN_EMAIL,
        hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
        full_name="Admin User",
        is_active=True,
        is_admin=True
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print(f"✓ Admin user created: {admin.email}")
    return admin


def seed_categories(db):
    """Seed sample categories with hierarchical structure"""
    print("Seeding categories...")
    
    # Check if categories exist
    if db.query(Category).count() > 0:
        print("✓ Categories already exist")
        return
    
    # Root categories
    electronics = Category(name="Electronics", slug="electronics", description="Electronic devices and accessories")
    clothing = Category(name="Clothing", slug="clothing", description="Apparel and fashion")
    books = Category(name="Books", slug="books", description="Books and publications")
    
    db.add_all([electronics, clothing, books])
    db.commit()
    
    # Electronics subcategories
    smartphones = Category(name="Smartphones", slug="smartphones", description="Mobile phones", parent_id=electronics.id)
    laptops = Category(name="Laptops", slug="laptops", description="Portable computers", parent_id=electronics.id)
    accessories = Category(name="Accessories", slug="accessories", description="Electronic accessories", parent_id=electronics.id)
    
    # Clothing subcategories
    mens = Category(name="Men's Wear", slug="mens-wear", description="Men's clothing", parent_id=clothing.id)
    womens = Category(name="Women's Wear", slug="womens-wear", description="Women's clothing", parent_id=clothing.id)
    
    db.add_all([smartphones, laptops, accessories, mens, womens])
    db.commit()
    
    print(f"✓ Created {db.query(Category).count()} categories")


def seed_products(db):
    """Seed sample products"""
    print("Seeding products...")
    
    # Check if products exist
    if db.query(Product).count() > 0:
        print("✓ Products already exist")
        return
    
    # Get categories
    smartphones_cat = db.query(Category).filter(Category.slug == "smartphones").first()
    laptops_cat = db.query(Category).filter(Category.slug == "laptops").first()
    
    products = [
        Product(
            name="iPhone 15 Pro",
            sku="IPHONE-15-PRO",
            description="Latest iPhone with A17 Pro chip",
            price=999.99,
            stock=50,
            status="active",
            category_id=smartphones_cat.id if smartphones_cat else None
        ),
        Product(
            name="Samsung Galaxy S24",
            sku="GALAXY-S24",
            description="Flagship Samsung smartphone",
            price=899.99,
            stock=40,
            status="active",
            category_id=smartphones_cat.id if smartphones_cat else None
        ),
        Product(
            name="MacBook Pro 14\"",
            sku="MBP-14-M3",
            description="MacBook Pro with M3 chip",
            price=1999.99,
            stock=30,
            status="active",
            category_id=laptops_cat.id if laptops_cat else None
        ),
        Product(
            name="Dell XPS 15",
            sku="DELL-XPS-15",
            description="Premium Windows laptop",
            price=1599.99,
            stock=25,
            status="active",
            category_id=laptops_cat.id if laptops_cat else None
        ),
        Product(
            name="AirPods Pro",
            sku="AIRPODS-PRO",
            description="Wireless earbuds with ANC",
            price=249.99,
            stock=100,
            status="active",
            category_id=None
        ),
        Product(
            name="Magic Mouse",
            sku="MAGIC-MOUSE",
            description="Apple wireless mouse",
            price=79.99,
            stock=75,
            status="active",
            category_id=None
        ),
        Product(
            name="USB-C Cable",
            sku="USB-C-CABLE",
            description="High-speed USB-C charging cable",
            price=19.99,
            stock=200,
            status="active",
            category_id=None
        ),
        Product(
            name="Wireless Charger",
            sku="WIRELESS-CHARGER",
            description="Qi wireless charging pad",
            price=39.99,
            stock=150,
            status="active",
            category_id=None
        )
    ]
    
    db.add_all(products)
    db.commit()
    
    print(f"✓ Created {len(products)} sample products")


def seed_test_user(db):
    """Seed a test user"""
    print("Seeding test user...")
    
    # Check if test user exists
    test_user = db.query(User).filter(User.email == "user@test.com").first()
    
    if test_user:
        print("✓ Test user already exists")
        return test_user
    
    # Create test user
    test_user = User(
        email="user@test.com",
        hashed_password=get_password_hash("Test@123"),
        full_name="Test User",
        is_active=True,
        is_admin=False
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    print(f"✓ Test user created: {test_user.email}")
    return test_user


def main():
    """Main seeder function"""
    print("\n" + "="*50)
    print("E-Commerce Database Seeder")
    print("="*50 + "\n")
    
    # Create tables
    create_tables()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Seed data
        seed_admin_user(db)
        seed_test_user(db)
        seed_categories(db)
        seed_products(db)
        
        print("\n" + "="*50)
        print("✓ Database seeding completed successfully!")
        print("="*50)
        print("\nDefault Credentials:")
        print(f"Admin: {settings.ADMIN_EMAIL} / {settings.ADMIN_PASSWORD}")
        print("Test User: user@test.com / Test@123")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    main()