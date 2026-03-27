from fastapi import FastAPI
from app.router.transaction import router as transaction_router
from app.router.customer import router_customers
from app.router.stats import router_stat
from app.router.system import router_system
from app.router.fraude import router_fraude
from app.config import connexion_dataset

app = FastAPI(
    title="Transaction API",
    description="API pour gérer les transactions et filtrage dynamique",
    version="1.0"
)

print("Chargement du dataset fusionné...")
app.state.df = connexion_dataset().head(100)
print(f"Dataset prêt : {len(app.state.df)} transactions chargées.")

app.include_router(transaction_router)
app.include_router(router_stat)
app.include_router(router_customers)
app.include_router(router_system)
app.include_router(router_fraude)

@app.get("/")
async def root():
    return {
        "message": "API Banking !",
        "status": "Ready",
        "total_records": len(app.state.df)
    }
