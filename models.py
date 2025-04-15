from pydantic import BaseModel
from sqlmodel import SQLModel, Field

class CustomerBase(BaseModel):
    name: str
    description: str | None
    email: str = Field(..., min_length=5, regex=r".+@.+\..+")
    age: int


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    id: int | None = None


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
