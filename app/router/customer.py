from fastapi import APIRouter, Query, Request
from typing import List, Dict, Any
from app.services.customers import list_customers, top_customers

router_customers = APIRouter(
    tags=["Customers"]
)


@router_customers.get("/api/customers", response_model=List[str])
def list_customers_route(request: Request):

    df = request.app.state.df
    return list_customers(df)


@router_customers.get("/api/customers/top", response_model=List[Dict[str, Any]])
def get_top_customers(request: Request, n: int = Query(10, gt=0)):

    df = request.app.state.df
    return top_customers(df, n=n)