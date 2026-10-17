from fastapi import Depends, FastAPI
from models import product
from config import SessionLocal,engine
import database
from sqlalchemy.orm import Session
app = FastAPI()

database.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def greet():
    return "Hello, welcome to the program!"

products = [
    product(id=1, name="Laptop", description="A high-performance laptop", price=1200.00, quantity=10),
    product(id=2, name="Smartphone", description="A latest model smartphone", price=800.00, quantity=20),
    product(id=3, name="Headphones", description="Noise-cancelling headphones", price=150.00, quantity=15),
    product(id=4, name="Smartwatch", description="A smartwatch with various features", price=200.00, quantity=25),
]

def init_db():
    db = SessionLocal()
    count = db.query(database.product).count()
    if count == 0:
        for prod in products:
            db.add(database.product(id=prod.id, name=prod.name, description=prod.description, price=prod.price, quantity=prod.quantity))
    db.commit()
    db.close()
init_db()

@app.get("/products")
def get_products(db: Session = Depends(get_db)):

    db_products = db.query(database.product).all()
    return db_products

@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(database.product).filter(database.product.id == id).first()
    if not product:
        return {"error": "Product not found"}
    return product

@app.post("/products")
def add_products(product: product, db: Session = Depends(get_db)):
    db.add(database.product(id=product.id, name=product.name, description=product.description, price=product.price, quantity=product.quantity))
    db.commit()
    db.refresh(database.product)
    return database.product

@app.put("/products/{id}")
def update_product(id: int, updated_product: product, db: Session = Depends(get_db)):
    product = db.query(database.product).filter(database.product.id == id).first()
    if not product:
        return {"error": "Product not found"}
    for key, value in updated_product.dict(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product
