# ./app/routers/customers.py

# Importing External Modules
from fastapi import APIRouter, status, HTTPException, Query, Depends
from sqlmodel import select
from sqlalchemy.orm import Session

# Importing Internal Modules
from models import (
    Customer,
    CustomerCreate,
    CustomerUpdate,
    Plan,
    CustomerPlan,
    StatusEnum,
    CustomerLogin
)
from app.utils.utils import hash_password, verify_password
from db import SessionDep

router = APIRouter()


# Endpoint para crear un cliente
@router.post("/customers", 
             response_model= Customer, 
             status_code=status.HTTP_201_CREATED
)
async def create_customer(
    customer_data: CustomerCreate, 
    session: SessionDep
):
    hashed_password = hash_password(customer_data.password)
    customer_data_dict = customer_data.model_dump()
    customer_data_dict['password_hash'] = hashed_password
    customer = Customer.model_validate(customer_data_dict)
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


@router.post("/customers/login")
async def login_customer(login_data: CustomerLogin, session: SessionDep):
    customer = session.exec(select(Customer).where(Customer.email == login_data.email)).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not verify_password(login_data.password, customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    return {"message": f"Login successful for {customer.name}"}


# Endpoint to subscribe a customer to a plan
@router.post("/customers/{customer_id}/plans/{plan_id}")
async def link_customer_to_plan(
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


# Endpoint to list the current plans for a customer filtered by status
@router.get("/customers/{customer_id}/plans", tags=["customers"])
async def get_current_customer_plans(
    customer_id: int,
    session: SessionDep,
    plan_status: StatusEnum = Query(StatusEnum.ACTIVE)  # Default to active
):

    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    # Get all CustomerPlan records for this customer
    query = select(CustomerPlan).where(CustomerPlan.customer_id == customer_id).order_by(CustomerPlan.id.desc())
    customer_plans = session.exec(query).all()

    # Keep only the latest record for each plan
    latest_plans = {}
    for cp in customer_plans:
        if cp.plan_id not in latest_plans:
            latest_plans[cp.plan_id] = cp

    result = []
    for customer_plan in latest_plans.values():
        if customer_plan.status == plan_status:
            plan = session.get(Plan, customer_plan.plan_id)
            if plan:
                result.append({
                    "plan_id": plan.id,
                    "plan_name": plan.name,
                    "status": customer_plan.status
                })

    return result


# Endpoint to set the status of a customer's plan (activate or deactivate)
@router.patch("/customers/{customer_id}/plans/{plan_id}/set", tags=["customers"])
async def set_plan_status_for_customer(
    customer_id: int,
    plan_id: int,
    session: SessionDep,
    plan_status: StatusEnum = Query()
):
    customer_db = session.get(Customer, customer_id)
    plan_db = session.get(Plan, plan_id)

    if not customer_db or not plan_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The customer or plan doesn't exist"
        )

    # Get the latest subscription record for this customer and plan
    query = select(CustomerPlan).where(
        CustomerPlan.customer_id == customer_id,
        CustomerPlan.plan_id == plan_id
    ).order_by(CustomerPlan.id.desc())

    last_customer_plan = session.exec(query).first()

    if not last_customer_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This customer is not linked to this plan yet"
        )

    # Insert a new record with the new status
    new_customer_plan = CustomerPlan(
        customer_id=customer_id,
        plan_id=plan_id,
        status=plan_status
    )

    session.add(new_customer_plan)
    session.commit()
    session.refresh(new_customer_plan)

    return {
        "detail": "Customer plan status updated successfully",
        "new_record_id": new_customer_plan.id
    }


# Endpoint to get the full history of plan subscriptions for a customer
@router.get("/customers/{customer_id}/plans/history")
async def get_customer_plans_history(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Customer not found"
        )
    
    query = select(CustomerPlan).where(CustomerPlan.customer_id == customer_id)
    customer_plans = session.exec(query).all()

    history = []
    for record in customer_plans:
        history.append({
            "plan_id": record.plan_id,
            "status": record.status
        })

    return history
