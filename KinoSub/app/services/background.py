from datetime import datetime, timedelta
from app.models import UserSubscription, User, Payment, Subscription, BalanceTransaction, Notification
from app.database import SessionLocal
import  uuid

def auto_renew_subscriptions():
    db = SessionLocal()
    today = datetime.utcnow().date()

    subs = db.query(UserSubscription).filter(
        UserSubscription.auto_renew == True,
        UserSubscription.end_date == today,
        UserSubscription.is_active == True
    ).all()

    for usub in subs:
        user = db.query(User).get(usub.user_id)
        sub = db.query(Subscription).get(usub.subscription_id)

        if user.balance >= sub.price:
            user.balance -= sub.price

            usub.start_date = today
            usub.end_date = today + timedelta(days=sub.duration_days)

            db.add(BalanceTransaction(
                user_id=user.id,
                amount=sub.price,
                type="withdraw",
                description=f"Автопродление подписки #{sub.id}"
            ))

            db.add(Payment(
                user_id=user.id,
                subscription_id=sub.id,
                amount=sub.price,
                status="completed",
                payment_method="balance",
                external_id=f"auto_{uuid.uuid4()}",
                created_at=datetime.utcnow()
            ))

            db.add(Notification(
                user_id=user.id,
                message=f"Подписка {sub.name} была автоматически продлена",
                is_read=False,
                created_at=datetime.utcnow()
            ))
        else:
            db.add(Notification(
                user_id=user.id,
                message=f"Недостаточно средств для автопродления подписки {sub.name}",
                is_read=False,
                created_at=datetime.utcnow()
            ))

    db.commit()
    db.close()
