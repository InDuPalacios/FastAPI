from fastapi import APIRouter, status, HTTPException
from sqlmodel import select

from models import Customer, CustomerCreate, CustomerUpdate, Plan, CustomerPlan
from db import SessionDep

router = APIRouter()


# Endpoint to list all registered customers
@router.post("/customers", response_model= Customer, tags=['customers'])
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


# Endpoint to list all registered customers
@router.get("/customers", response_model=list[Customer], tags=['customers'])
async def list_customer(session: SessionDep):
    return session.exec(select(Customer)).all()


# Endpoint to get a single customer by ID
@router.get("/customers/{customer_id}", response_model=Customer, tags=['customers'])
async def read_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Customer not found")
    return customer


# Endpoint to delete a specific customer by ID
@router.delete("/customers/{customer_id}", tags=['customers'])
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


@router.post("/customers/{customer_id}/plans/{plan_id}")
async def suscribe_customer_to_plan(
        customer_id: int, 
        plan_id: int,
        session: SessionDep
    ):
    customer_db = session.get(Customer, customer_id)
    plan_db = session.get(Plan, plan_id)

    if not customer_db or not plan_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="The customer or plan doesn't exist"
        )
    customer_plan_db = CustomerPlan(plan_id=plan_db.id, customer_id=customer_db.id)

    session.add(customer_plan_db)
    session.commit()
    session.refresh(customer_plan_db)
    return customer_plan_db
    

@router.get("/customers/{customer_id}/plans")
async def get_customer_plan(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return customer_db.plans