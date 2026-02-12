from fastapi import FastAPI
from app.router.transaction import router as transaction_router
from app.router.customer import router_customers
from app.router.stats import router_stat
from app.router.system import router_system
from app.router.fraude import router_fraude 

# Création de l'application FastAPI
app = FastAPI(
    title="Transaction API",
    description="API pour gérer les transactions et filtrage dynamique",
    version="1.0"
)

# Inclusion du router
app.include_router(transaction_router)
app.include_router(router_stat) 
app.include_router(router_customers)
app.include_router(router_system)
app.include_router(router_fraude)# Optionnel : route racine pour tester si l'API est active
@app.get("/")
async def root():
    return {"message": "API Banking !"}
