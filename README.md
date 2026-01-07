# E-Commerce Backend API

> FastAPI-based e-commerce backend with multi-provider payment support (Stripe & bKash)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Requirements Met](#requirements-met)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Payment Flow](#payment-flow)
- [Testing](#testing)
- [Deployment](#deployment)

---

## ✨ Features

### Core Features
- ✅ **User Management**: Registration, login, JWT authentication
- ✅ **Product Management**: CRUD operations with admin authorization
- ✅ **Order Management**: Multi-item orders with stock validation
- ✅ **Payment Integration**: Stripe & bKash support via Strategy Pattern
- ✅ **Category Hierarchy**: DFS traversal with Redis caching
- ✅ **Webhook Handling**: Async payment status updates

### Design Patterns & Algorithms
- ✅ **OOP Classes**: Service layer architecture (User, Product, Order, Payment services)
- ✅ **Strategy Pattern**: Payment provider abstraction
- ✅ **DFS Algorithm**: Category tree traversal
- ✅ **Redis Caching**: Optimized category tree queries
- ✅ **Deterministic Algorithms**: Total/subtotal calculation, stock reduction

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI 0.109.0 |
| **Database** | PostgreSQL 15 |
| **ORM** | SQLAlchemy 2.0 |
| **Migrations** | Alembic |
| **Cache** | Redis 7 |
| **Auth** | JWT (python-jose) |
| **Payment** | Stripe SDK, bKash API |
| **Testing** | Pytest |
| **Container** | Docker & Docker Compose |

---

## 📁 Project Structure

```
ecommerce-backend/
├── app/
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   └── payment.py
│   │
│   ├── schemas/              # Pydantic schemas
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── payment.py
│   │
│   ├── services/             # Business logic (OOP)
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   └── payment_service.py
│   │
│   ├── payment_providers/    # Strategy Pattern
│   │   ├── base.py
│   │   ├── stripe_provider.py
│   │   ├── bkash_provider.py
│   │   └── __init__.py (Factory)
│   │
│   ├── api/v1/endpoints/     # API routes
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── products.py
│   │   ├── categories.py
│   │   ├── orders.py
│   │   └── payments.py
│   │
│   ├── core/                 # Core utilities
│   │   ├── security.py       # JWT, password hashing
│   │   ├── dependencies.py   # FastAPI dependencies
│   │   └── cache.py          # Redis wrapper
│   │
│   ├── utils/
│   │   └── dfs.py            # DFS category traversal
│   │
│   ├── main.py               # FastAPI app
│   ├── config.py             # Settings
│   └── database.py           # DB connection
│
├── scripts/
│   └── seed_data.py          # Database seeder
│
├── alembic/                  # Database migrations
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## ✅ Requirements Met

### Functional Requirements

| Requirement | Status | Implementation |
|------------|--------|----------------|
| User Management | ✅ | `UserService`, JWT auth, email uniqueness |
| Product Management | ✅ | `ProductService`, admin-only CRUD, SKU uniqueness |
| Order Management | ✅ | `OrderService`, multi-item orders, status tracking |
| Payment System | ✅ | Stripe & bKash integration, webhook handlers |
| Payment Table | ✅ | `Payment` model with provider, transaction_id, status |
| Order Flow | ✅ | Create → Choose provider → Pay → Update status → Reduce stock |

### Design Requirements

| Requirement | Status | Implementation |
|------------|--------|----------------|
| OOP Classes | ✅ | Service layer: `UserService`, `ProductService`, `OrderService`, `PaymentService` |
| Data Structures | ✅ | Relational tables with foreign keys and indexes |
| Algorithms | ✅ | Deterministic total/subtotal calculation, stock reduction |
| Strategy Pattern | ✅ | `PaymentProvider` base class, `PaymentFactory` |
| DFS + Caching | ✅ | `CategoryTree.build_tree()` with Redis cache |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd ecommerce-backend

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Start all services
docker-compose up --build

# Run migrations (in another terminal)
docker-compose exec backend alembic upgrade head

# Seed database
docker-compose exec backend python scripts/seed_data.py
```

Access API: **http://localhost:8000/docs**

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL and Redis
# Update .env with connection strings

# Run migrations
alembic upgrade head

# Seed database
python scripts/seed_data.py

# Start server
uvicorn app.main:app --reload
```

### Default Credentials

```
Admin User:
Email: admin@ecommerce.com
Password: Admin@123

Test User:
Email: user@test.com
Password: Test@123
```

---

## 📚 API Documentation

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
```http
POST /api/v1/auth/register
POST /api/v1/auth/login
```

#### Products
```http
GET    /api/v1/products          # List products (paginated, filterable)
GET    /api/v1/products/{id}     # Get product details
POST   /api/v1/products          # Create product (Admin)
PUT    /api/v1/products/{id}     # Update product (Admin)
DELETE /api/v1/products/{id}     # Delete product (Admin)
```

#### Orders
```http
POST   /api/v1/orders            # Create order
GET    /api/v1/orders            # Get user's orders
GET    /api/v1/orders/{id}       # Get order details
POST   /api/v1/orders/{id}/cancel # Cancel order
```

#### Payments
```http
POST   /api/v1/payments/create          # Create payment
POST   /api/v1/payments/confirm         # Confirm payment
GET    /api/v1/payments/{id}            # Get payment status
POST   /api/v1/payments/webhooks/stripe # Stripe webhook
POST   /api/v1/payments/webhooks/bkash  # bKash webhook
```

#### Categories (DFS + Cache)
```http
GET    /api/v1/categories/tree          # Get category tree (cached)
GET    /api/v1/categories/{id}/path     # Get category path
GET    /api/v1/categories/{id}/related  # Get related categories
POST   /api/v1/categories/cache/invalidate # Clear cache
```

---

## 💳 Payment Flow

### Order & Payment Process

```
1. User creates order
   POST /api/v1/orders
   {
     "items": [
       {"product_id": 1, "quantity": 2}
     ]
   }
   → Order created with PENDING status

2. User initiates payment
   POST /api/v1/payments/create
   {
     "order_id": 1,
     "provider": "stripe"  # or "bkash"
   }
   → Returns payment intent/checkout URL

3a. Stripe Flow:
    - Frontend uses client_secret with Stripe Elements
    - User completes payment
    - Stripe sends webhook → /api/v1/payments/webhooks/stripe
    - System updates payment status to SUCCESS
    - Order status → PAID
    - Stock reduced

3b. bKash Flow:
    - Redirect user to bkash_url
    - User completes payment in bKash
    - bKash redirects to callback → /api/v1/payments/webhooks/bkash
    - System executes payment
    - Order status → PAID
    - Stock reduced
```

### Strategy Pattern Implementation

```python
# Payment providers implement common interface
class PaymentProvider(ABC):
    def create_payment(...)
    def confirm_payment(...)
    def query_payment(...)
    def handle_webhook(...)

# Factory selects provider at runtime
provider = PaymentFactory.get_provider("stripe")  # or "bkash"
result = provider.create_payment(amount, order_id)
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest app/tests/test_orders.py -v
```

### Test Coverage

```bash
# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Manual API Testing

Use the Swagger UI at http://localhost:8000/docs

**Test Flow:**
1. Register user → `/auth/register`
2. Login → `/auth/login` (copy access_token)
3. Click "Authorize" button, paste token
4. Create order → `/orders`
5. Create payment → `/payments/create`
6. Confirm payment → `/payments/confirm`

---

## 🚀 Deployment

### Local with ngrok (for webhooks)

```bash
# Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000

# In another terminal, start ngrok
ngrok http 8000

# Copy the ngrok URL (e.g., https://abc123.ngrok.io)
# Configure webhook URLs in Stripe/bKash dashboard:
# - Stripe: https://abc123.ngrok.io/api/v1/payments/webhooks/stripe
# - bKash: https://abc123.ngrok.io/api/v1/payments/webhooks/bkash
```

### Docker Production

```bash
# Build image
docker build -t ecommerce-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e REDIS_URL="redis://..." \
  -e SECRET_KEY="..." \
  -e STRIPE_SECRET_KEY="..." \
  ecommerce-backend
```

### Environment Variables

**Required:**
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `BKASH_APP_KEY`
- `BKASH_APP_SECRET`
- `BKASH_USERNAME`
- `BKASH_PASSWORD`

See `.env.example` for complete list.

---

## 📖 Additional Documentation

### ERD Diagram

```
Users
├── id (PK)
├── email (unique)
├── hashed_password
├── is_admin
└── Orders (1:N)

Products
├── id (PK)
├── sku (unique)
├── name
├── price
├── stock
├── category_id (FK)
└── OrderItems (1:N)

Categories
├── id (PK)
├── name
├── parent_id (FK, self-referential)
└── Products (1:N)

Orders
├── id (PK)
├── user_id (FK)
├── total_amount
├── status
├── OrderItems (1:N)
└── Payments (1:N)

OrderItems
├── id (PK)
├── order_id (FK)
├── product_id (FK)
├── quantity
├── price
└── subtotal

Payments
├── id (PK)
├── order_id (FK)
├── provider (stripe/bkash)
├── transaction_id (unique)
├── status
└── raw_response (JSON)
```

### DFS Algorithm Implementation

The category tree uses Depth-First Search (DFS) for traversal:

```python
def _dfs_traverse(category, category_map):
    node = {
        "id": category.id,
        "name": category.name,
        "children": []
    }
    
    # Find children
    children = [cat for cat in category_map.values() 
                if cat.parent_id == category.id]
    
    # Recursive DFS
    for child in children:
        node["children"].append(_dfs_traverse(child, category_map))
    
    return node
```

**Caching:** Results cached in Redis for 1 hour to minimize database queries.

---

## 📝 Notes

### Payment Provider Setup

**Stripe:**
1. Create account at https://stripe.com
2. Get test API keys from dashboard
3. Configure webhook endpoint
4. Update `.env` with keys

**bKash:**
1. Request sandbox credentials from bKash
2. Configure sandbox environment
3. Set callback URL
4. Update `.env` with credentials

### Stock Management

Stock is reduced **only after successful payment**:
1. Order created → Stock **NOT** reduced (still in PENDING)
2. Payment confirmed → Order marked as PAID → Stock reduced

This prevents stock reservation issues with abandoned carts.

---

## 🤝 Contributing

This is an assessment project. For production use, consider:
- Add comprehensive test suite
- Implement rate limiting
- Add request validation middleware
- Setup monitoring (Sentry, DataDog)
- Implement proper logging
- Add API versioning strategy
- Setup CI/CD pipeline

---

## 📄 License

This project is created for assessment purposes.

---

## 📧 Support

For questions or issues:
1. Check API documentation at `/docs`
2. Review error responses (following REST standards)
3. Check logs: `docker-compose logs backend`

**Assessment Submission Checklist:**
- ✅ Complete codebase with all requirements
- ✅ Docker deployment setup
- ✅ Database seeder with sample data
- ✅ API documentation (Swagger)
- ✅ ERD and architecture docs
- ✅ README with setup instructions
- ✅ .env.example template
- ✅ Testing guide#   E - C o m m e r c e - B a c k e n d - A s s e s s m e n t  
 #   A s s e s s m e n t - E - C o m m e r c e - B a c k e n d  
 