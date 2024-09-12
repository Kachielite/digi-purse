from sqlalchemy.orm import Session

from app.models.Loyalty import Loyalty
from app.models.Transaction import Transaction
from app.models.Wallet import Wallet
from app.schemas.LoyaltySchemas import LoyaltyRedeemSchema
from app.utilities.check_role import check_admin_user

# Define a conversion rate
# POINTS_TO_CASH_RATE = 0.01  # 1 point = $0.01
# MINIMUM_REDEEM_POINTS = 100  # Minimum points to redeem

POINTS_TO_CASH_RATE = 0.01  # 1 point = $0.01
MINIMUM_REDEEM_POINTS = 10  # Minimum points to redeem


# Check if user is an admin or wallet owner
def is_admin_or_user_owner(user: dict, user_id: int):
    if user is None:
        return False

    admin_user = check_admin_user(user)
    user_owner = user.get("user_id") == user_id

    if admin_user or user_owner:
        return True
    else:
        return False


# Read all loyalties
def read_all_loyalties(db: Session, user: dict, limit, offset):
    if check_admin_user(user) is None:
        return 401, {"message": "You do not have enough permission to read loyalties"}

    loyalties = db.query(Loyalty).offset(offset).limit(limit).all()

    loyalties_response = [
        {
            "id": loyalty.id,
            "user_id": loyalty.user_id,
            "points": loyalty.points,
            "created_at": loyalty.created_at.isoformat(timespec='milliseconds') + 'Z',
            "updated_at": loyalty.updated_at.isoformat(timespec='milliseconds') + 'Z'
        }
        for loyalty in loyalties
    ]
    return 200, loyalties_response


# Read user loyalty
def read_user_loyalty(db: Session, user: dict, user_id: int):
    if not is_admin_or_user_owner(user, user_id):
        return 401, {"message": "You do not have enough permission to read this loyalty"}

    loyalty = db.query(Loyalty).filter(Loyalty.user_id == user_id).first()

    if loyalty is None:
        return 404, {"message": "Loyalty not found"}

    loyalty_response = {
        "id": loyalty.id,
        "user_id": loyalty.user_id,
        "points": loyalty.points,
        "created_at": loyalty.created_at.isoformat(timespec='milliseconds') + 'Z',
        "updated_at": loyalty.updated_at.isoformat(timespec='milliseconds') + 'Z'
    }
    return 200, loyalty_response


# Redeem loyalty points
def redeem_loyalty_points(db: Session, user: dict, loyalty_redeem: LoyaltyRedeemSchema):
    if not is_admin_or_user_owner(user, loyalty_redeem.user_id):
        return 401, {"message": "You do not have enough permission to redeem loyalty points"}

    loyalty = db.query(Loyalty).filter(Loyalty.user_id == loyalty_redeem.user_id).first()

    if loyalty is None:
        return 404, {"message": "Loyalty not found"}

    if loyalty.points < MINIMUM_REDEEM_POINTS:
        return 400, {"message": f"Minimum points to redeem is {MINIMUM_REDEEM_POINTS}"}

    if loyalty.points < loyalty_redeem.quantity:
        return 400, {"message": "Insufficient points to redeem"}

    # Calculate cash equivalent
    cash_equivalent = loyalty_redeem.quantity * POINTS_TO_CASH_RATE

    # Deduct points
    loyalty.points -= loyalty_redeem.quantity

    # Top up wallet

    wallet = db.query(Wallet).filter(Wallet.user_id == loyalty.user_id).first()
    wallet.balance += cash_equivalent

    transaction = Transaction(
        type="credit",
        amount=cash_equivalent,
        wallet_id=wallet.id,
        source="LOYALTY_REDEMPTION",
        description="Top up wallet from loyalty points redemption",
    )

    db.add(loyalty)
    db.add(wallet)
    db.add(transaction)
    db.commit()

    return 201, {"message": f"Points redeemed successfully. Cash equivalent: ${cash_equivalent}"}
