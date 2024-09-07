from enum import Enum


class TransactionEnum(str, Enum):
    CREDIT = "credit"
    BALANCE = "balance"
    DEBIT = "debit"
    REFUND = "refund"