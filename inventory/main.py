from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis_om import HashModel, NotFoundError
from database import redis  # Uvozimo spremnu konekciju
from typing import List
from config import settings  

app = FastAPI(title="Inventory Service")

#Treba nam CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_methods=['*'],
    allow_headers=['*']
)

# Model sada koristi database.redis
# I bice jedna tabela u Redis DB
class Product(HashModel, index=True):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

def format_product(pk: str):
    """Pomoćna funkcija za mapiranje Redis objekta u rečnik"""
    product = Product.get(pk)
    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }

@app.get('/products', response_model=List[dict])
async def all_products():
    """Vraća listu svih primarnih ključeva i formatira ih"""
    return [format_product(pk) for pk in Product.all_pks()]

@app.post('/products')
async def create(product: Product):
    """Automatska validacija ulaznih podataka putem Pydantic-a"""
    return product.save()

@app.get('/products/{pk}')
async def get_one(pk: str):
    """Rukovanje greškom ako proizvod ne postoji - vitalno za API standarde"""
    try:
        return Product.get(pk)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")

@app.delete('/products/{pk}')
async def delete(pk: str):
    """Brisanje zapisa na osnovu primarnog ključa"""
    return Product.delete(pk)