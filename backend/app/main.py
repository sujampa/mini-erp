from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Database models
from app.models.product import Product
from app.models.inventory_transaction import InventoryTransaction
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem

# API routers
from app.api.products import router as product_router
from app.api.inventory import router as inventory_router
from app.api.sales_order import router as sales_order_router
from app.api.suppliers import router as suppliers_router
from app.api.purchase_orders import router as purchase_orders_router
from app.api.dashboard import router as dashboard_router
from app.api.auth import router as auth_router
from app.api.ai_assistant import router as ai_assistant_router
# Business rule exceptions
from app.core.exceptions import BusinessRuleError


# Initialize FastAPI application
app = FastAPI(
    title="Mini ERP",
    description="AI-powered Mini ERP backend",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Handle business rule violations
@app.exception_handler(BusinessRuleError)
async def business_rule_exception_handler(
    request: Request,
    exc: BusinessRuleError,
):
    return JSONResponse(
        status_code=409,
        content={
            "error": "Business rule violation",
            "detail": exc.message,
        },
    )


# Register API routers
app.include_router(product_router)
app.include_router(inventory_router)
app.include_router(sales_order_router)
app.include_router(suppliers_router)
app.include_router(purchase_orders_router)
app.include_router(dashboard_router)
app.include_router(auth_router)
app.include_router(ai_assistant_router)

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "mini-erp-backend",
        "version": "0.1.0",
    }