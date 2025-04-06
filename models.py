from pydantic import BaseModel
from sqlmodel import SQLModel

# Base model with shared customer fields
class CustomerBase(SQLModel):
    name: str
    description: str | None
    email: str
    age: int

# Model used when creating a new customer (input only)
class CustomerCreate(CustomerBase):
    pass

# Model representing a customer with an optional ID (used in DB responses)
class Customer(SQLModel, table=True):
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
