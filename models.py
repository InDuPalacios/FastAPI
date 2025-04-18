from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class CustomerBase(SQLModel):
    name: str = Field(default= None)
    description: str | None = Field(default= None)
    email: str = Field(..., min_length=5, regex=r".+@.+\..+")
    age: int = Field(default= None)


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase, table= True):
    id: int | None = Field(default= None, primary_key= True)


# Model representing a single transaction
class Transaction(BaseModel):
    id: int
    ammount: int
    description: str


# Model representing an invoice that contains a list of transactions
class Invoice(BaseModel):
    id: int
    customer: Customer
    transactions: list[Transaction]
    total: int
    
    @property
    def ammount_total(self):
        """
        Calculates the total amount from all transactions.
        """
        return sum(transaction.ammount for transaction in self.transactions)
