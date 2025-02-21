from fastapi import FastAPI
from app.routes.product_routes import router as product_router
from app.routes.user_routes import router as user_router
from app.routes.health_routes import router as health_router
from app.routes.supplier_routes import router as supplier_router
from app.routes.purchase_routes import router as purchase_router
from app.routes.bank_account_routes import router as bank_account_router
from app.routes import stats_routes

app = FastAPI(
    title="FastAPI MongoDB API",
    description="A simple REST API using FastAPI and MongoDB",
    version="1.0.0"
)

app.include_router(health_router, tags=["Health"])
app.include_router(product_router, tags=["Products"])
app.include_router(user_router, tags=["Users"])
app.include_router(supplier_router, tags=["Suppliers"])
app.include_router(purchase_router, tags=["Purchases"])
app.include_router(bank_account_router, tags=["bank_accounts"])
app.include_router(stats_routes.router, tags=["Statistics"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the FastAPI MongoDB API!"}
