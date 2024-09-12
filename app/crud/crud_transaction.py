from sqlalchemy.orm import Session

from app.models.Transaction import Transaction
from app.models.Wallet import Wallet
from app.schemas.TransactionSchemas import TransactionRequest
from app.utilities.check_role import check_admin_user


# top up wallet
def top_wallet(db: Session, user: dict, request: TransactionRequest):
    if check_admin_user(user) is None:
        return 403, {"message": "Unauthorized access"}

    wallet_to_be_credited = db.query(Wallet).filter(Wallet.user_phone_number == request.destination).first()

    if not wallet_to_be_credited or wallet_to_be_credited.is_deleted:
        return 404, {"message": "Wallet not found"}

    wallet_to_be_credited.balance += request.amount

    transaction = Transaction(
        type="credit",
        amount=request.amount,
        wallet_id=wallet_to_be_credited.id,
        source=request.source,
        description=f"Top up wallet by System Admin: {user.get('username')}",
    )

    db.add(wallet_to_be_credited)
    db.add(transaction)
    db.commit()
    return 200, {"message": "Wallet topped up successfully"}


# debit wallet
def debit_wallet(db: Session, user: dict, request: TransactionRequest):
    if check_admin_user(user) is None:
        return 403, {"message": "Unauthorized access"}

    wallet_to_be_debited = db.query(Wallet).filter(Wallet.user_phone_number == request.destination).first()

    if not wallet_to_be_debited or wallet_to_be_debited.is_deleted:
        return 404, {"message": "Wallet not found"}

    if wallet_to_be_debited.user_id == user.get("user_id"):
        return 400, {"message": "You cannot debit your own wallet"}

    if wallet_to_be_debited.is_blocked:
        return 403, {"message": "Wallet is blocked"}

    if wallet_to_be_debited.balance < request.amount:
        return 400, {"message": "Insufficient balance"}

    wallet_to_be_debited.balance -= request.amount

    transaction = Transaction(
        type="debit",
        amount=request.amount,
        wallet_id=wallet_to_be_debited.id,
        source=request.source,
        description=f"Debit wallet by System Admin: {user.get('username')}",
    )

    db.add(wallet_to_be_debited)
    db.add(transaction)
    db.commit()
    return 200, {"message": "Wallet debited successfully"}


# get all transactions
def transaction_all_history(db: Session, user: dict, limit: int = 10, offset: int = 0):
    if check_admin_user(user) is None:
        return 403, {"message": "Unauthorized access"}

    transactions = db.query(Transaction).offset(offset).limit(limit).all()

    transactions_response = [
        {
            "id": str(transaction.id),
            "wallet_id": str(transaction.wallet_id),
            "amount": transaction.amount,
            "type": transaction.type,
            "description": transaction.description,
            "source": transaction.source,
            "created_at": transaction.created_at.isoformat(timespec='milliseconds') + 'Z',
            "updated_at": transaction.updated_at.isoformat(timespec='milliseconds') + 'Z'
        } for transaction in transactions
    ]

    return 200, transactions_response


# get user transactions
def transaction_user_history(db: Session, user: dict, user_id: str, limit: int = 10, offset: int = 0):
    if check_admin_user(user) is None:
        return 403, {"message": "Unauthorized access"}

    user_wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()

    if not user_wallet or user_wallet.is_deleted:
        return 404, {"message": "User wallet"}

    if user_wallet.is_blocked:
        return 403, {"message": "User wallet is blocked"}

    transactions = (db.query(Transaction).filter(Transaction.wallet_id == user_wallet.id).offset(offset).limit(limit)
                    .all())

    transactions_response = [
        {
            "id": str(transaction.id),
            "wallet_id": str(transaction.wallet_id),
            "amount": transaction.amount,
            "type": transaction.type,
            "description": transaction.description,
            "source": transaction.source,
            "created_at": transaction.created_at.isoformat(timespec='milliseconds') + 'Z',
            "updated_at": transaction.updated_at.isoformat(timespec='milliseconds') + 'Z'
        } for transaction in transactions
    ]

    return 200, transactions_response


# get transaction by id
def transaction_by_id(db: Session, user: dict, transaction_id: str):
    print(f"transaction_id: {transaction_id}")
    if check_admin_user(user) is None:
        return 403, {"message": "Unauthorized access"}

    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        return 404, {"message": "Transaction not found"}

    transaction_response = {
        "id": str(transaction.id),
        "wallet_id": str(transaction.wallet_id),
        "amount": transaction.amount,
        "type": transaction.type,
        "description": transaction.description,
        "source": transaction.source,
        "created_at": transaction.created_at.isoformat(timespec='milliseconds') + 'Z',
        "updated_at": transaction.updated_at.isoformat(timespec='milliseconds') + 'Z'
    }

    return 200, transaction_response
