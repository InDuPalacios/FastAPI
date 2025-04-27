from fastapi import APIRouter, status, HTTPException, Query
from sqlmodel import select

from models import Customer, CustomerCreate, CustomerUpdate, Plan, CustomerPlan, StatusEnum
from db import SessionDep

router = APIRouter()


# Endpoint to list all registered customers
@router.post("/customers", response_model= Customer)
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


# Endpoint to list all registered customers
@router.get("/customers", response_model=list[Customer])
async def list_customer(session: SessionDep):
    return session.exec(select(Customer)).all()


# Endpoint to get a single customer by ID
@router.get("/customers/{customer_id}", response_model=Customer)
async def read_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Customer not found")
    return customer


# Endpoint to delete a specific customer by ID
@router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Customer not found")
    session.delete(customer)
    session.commit()
    return {"detal":"ok"}


# Endpoint to update an existing customer by ID
@router.patch(
        "/customers/{customer_id}", 
        response_model=Customer, 
        status_code=status.HTTP_201_CREATED, 
        tags=['customers']
)
async def update_customer(
    customer_id: int,
    updated_data: CustomerUpdate,
    session: SessionDep
):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    # Use sqlmodel_update to update fields in one step
    customer.sqlmodel_update(updated_data.model_dump(exclude_unset=True))
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


# Endpoint to subscribe a customer to a plan
@router.post("/customers/{customer_id}/plans/{plan_id}")
async def suscribe_customer_to_plan(
        customer_id: int, 
        plan_id: int,
        session: SessionDep,
        plan_status:StatusEnum = Query()
    ):
    customer_db = session.get(Customer, customer_id)
    plan_db = session.get(Plan, plan_id)

    if not customer_db or not plan_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="The customer or plan doesn't exist"
        )
    customer_plan_db = CustomerPlan(plan_id=plan_db.id, 
                                    customer_id=customer_db.id,
                                    status= plan_status)

    session.add(customer_plan_db)
    session.commit()
    session.refresh(customer_plan_db)
    return customer_plan_db
    

# Endpoint to get customer's plans filtered by status
@router.get("/customers/{customer_id}/plans")
async def get_customer_plan(
    customer_id: int, session: SessionDep, plan_status: StatusEnum = Query()
):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    query = (
        select(CustomerPlan)
        .where(CustomerPlan.customer_id == customer_id)
        .where(CustomerPlan.status == plan_status)
    )
    plans = session.exec(query).all()
    return plans


# Endpoint to unsubscribe a customer from a plan
@router.patch("/customers/{customer_id}/plans/{plan_id}/unsubscribe")
async def unsubscribe_customer_from_plan(customer_id: int, plan_id: int, session: SessionDep):
    query = select(CustomerPlan).where(
        CustomerPlan.customer_id == customer_id,
        CustomerPlan.plan_id == plan_id,
        CustomerPlan.status == StatusEnum.ACTIVE  # Aseguramos que esté activo
    )
    customer_plan = session.exec(query).first()

    if not customer_plan:
        raise HTTPException(status_code=404, detail="Subscription not found or already inactive")

    customer_plan.status = StatusEnum.INACTIVE
    session.add(customer_plan)
    session.commit()
    session.refresh(customer_plan)

    return {"detail": "Customer unsubscribed successfully"}
