from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.Wallet import Wallet
from app.schemas.WalletSchemas import WalletCreationRequest, WalletUpdateRequest
from app.utilities.check_role import check_admin_user

no_read_permission = "You do not have enough permission to read wallets"


# Check if user is an admin or wallet owner
def is_admin_or_wallet_owner(user: dict, user_id: int):
    admin_user = check_admin_user(user)
    wallet_owner = user.get("user_id") == user_id

    if admin_user or wallet_owner:
        return True
    else:
        return False


# Create wallet
def create_wallet(db: Session, user: dict, wallet: WalletCreationRequest):
    if check_admin_user(user) is None:
        return 401, {"message": "You do not have enough permission to create wallets"}

    user_id_exists = db.query(Wallet).filter(Wallet.user_id == wallet.user_id).first()
    user_phone_number_exists = db.query(Wallet).filter(Wallet.user_phone_number == wallet.user_phone_number).first()

    if user_id_exists and user_phone_number_exists:
        return 400, {"message": "User already has a wallet"}


    request = Wallet(
        user_id=wallet.user_id,
        user_phone_number=wallet.user_phone_number
    )

    db.add(request)
    db.commit()
    return 201, {"message": "Wallet created successfully"}


# Read wallet details
def read_wallet_details(db: Session, user: dict, user_id: int | None, wallet_id: str | None, phone_number: str | None):
    # Ensure at least one identifier is provided
    if not any([user_id, wallet_id, phone_number]):
        return 400, {"message": "At least one of user_id, wallet_id, or phone_number must be provided"}

    if not is_admin_or_wallet_owner(user, user_id):
        return 401, {"message": no_read_permission}

    # Build the query with 'or_' to match any of the provided parameters
    wallet_info = db.query(Wallet).filter(
        Wallet.is_deleted == False,
        or_(
            Wallet.user_id == user_id,
            Wallet.id == wallet_id,
            Wallet.user_phone_number == phone_number
        )
    ).first()

    if wallet_info is None:
        return 404, {"message": "User wallet details not found"}

    wallet_blocked = wallet_info.is_blocked is True

    if wallet_blocked:
        return 403, {"message": "Wallet is blocked. Please contact support for more information"}

    wallet_info_response = {
        "id": str(wallet_info.id),
        "user_id": wallet_info.user_id,
        "user_phone_number": wallet_info.user_phone_number,
        "balance": wallet_info.balance,
        "is_blocked": wallet_info.is_blocked,
        "is_deleted": wallet_info.is_deleted,
        "created_at": wallet_info.created_at.isoformat(timespec='milliseconds') + 'Z',
        "updated_at": wallet_info.updated_at.isoformat(timespec='milliseconds') + 'Z'
    }

    return 200, wallet_info_response


# Read all wallets
def read_all_wallet(db: Session, user: dict, limit: int = 10, offset: int = 0):
    if check_admin_user(user) is None:
        return 401, {"message": no_read_permission}

    wallets_info = db.query(Wallet).filter(Wallet.is_deleted == False).offset(offset).limit(limit).all()

    wallets_info_response = [
        {
            "id": str(wallet.id), # Convert UUID to string
            "user_id": wallet.user_id,
            "user_phone_number": wallet.user_phone_number,
            "balance": wallet.balance,
            "is_blocked": wallet.is_blocked,
            "is_deleted": wallet.is_deleted,
            "created_at": wallet.created_at.isoformat(timespec='milliseconds') + 'Z',
            "updated_at": wallet.updated_at.isoformat(timespec='milliseconds') + 'Z'
        } for wallet in wallets_info
    ]
    return 200, wallets_info_response


# Block or unblock wallet
def block_user_wallet(user: dict, db: Session, wallet_id: str, wallet_update: WalletUpdateRequest):
    if not check_admin_user(user):
        return 401, {"message": "You do not have enough permission to block wallets"}

    user_wallet = db.query(Wallet).filter(and_(Wallet.id == wallet_id, Wallet.is_deleted == False)).first()

    if user_wallet is None:
        return 404, {"message": "User wallet not found"}

    if user_wallet.is_blocked is wallet_update.is_blocked:
        wallet_block_state = "blocked" if wallet_update.is_blocked else "unblocked"
        return 400, {"message": f"Wallet is already {wallet_block_state}"}

    user_wallet.is_blocked = wallet_update.is_blocked

    db.add(user_wallet)
    db.commit()

    wallet_block_state = "blocked" if wallet_update.is_blocked else "unblocked"

    return 200, {"message": f"Wallet {wallet_block_state} successfully"}


# Delete wallet
def delete_user_wallet(db: Session, user: dict, wallet_id: str):
    if check_admin_user(user) is None:
        return 401, {"message": "You do not have enough permission to delete wallets"}

    user_wallet = db.query(Wallet).filter(and_(Wallet.id == wallet_id, Wallet.is_deleted == False)).first()

    if user_wallet is None:
        return 404, {"message": "User wallet not found"}

    user_wallet.is_deleted = True

    db.add(user_wallet)
    db.commit()

    return 200, {"message": "Wallet deleted successfully"}
