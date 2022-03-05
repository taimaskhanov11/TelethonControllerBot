import datetime

from loguru import logger
from tortoise import fields, models

from telethoncontrollerbot.config.config import TZ


class DbUser(models.Model):
    user_id = fields.IntField(index=True)
    username = fields.CharField(max_length=255)
    subscription = fields.OneToOneField("models.Subscription", related_name="db_user")
    register_data = fields.DatetimeField()

    @classmethod
    async def get_or_new(cls, user_id, username) -> "DbUser":
        user = await cls.get_or_none(user_id=user_id).select_related("subscription")
        is_created = False
        if not user:
            user = await cls.create(
                user_id=user_id,
                username=username,
                subscription=await Subscription.create(),
                register_data=datetime.datetime.now(TZ),
            )
            is_created = True

        if is_created:
            logger.info(f"Создание нового пользователя {user_id} {username}")
        return user


class Subscription(models.Model):
    title = fields.CharField(max_length=255, default="Нет подписки")
    is_subscribe = fields.BooleanField(default=False)
    is_paid = fields.BooleanField(default=True)
    duration = fields.IntField(default=0)


class SubscriptionInfo(models.Model):
    title = fields.CharField(max_length=255)
    price = fields.IntField()
    days = fields.IntField()

    def __str__(self):
        return (
            # f"ID: {self.pk}\n"
            f"Название : {self.title}\n"
            f"Цена: {self.price}\n"
            f"Количество дней: {self.days}\n"
        )


class Billing(models.Model):
    db_user = fields.OneToOneField(
        "models.DbUser",
    )
    # bill_id = fields.BigIntField(index=True)
    bill_id = fields.CharField(max_length=255)
    amount = fields.IntField()
    subscription = fields.OneToOneField("models.Subscription")

    @classmethod
    async def create_bill(cls, db_user, bill_id, sub_info: SubscriptionInfo):
        subscription = await Subscription.create(
            title=sub_info.title,
            # is_subscribe=True,
            is_paid=False,
            duration=sub_info.days,
        )
        return await cls.create(
            db_user=db_user,
            bill_id=bill_id,
            amount=sub_info.price,
            subscription=subscription,
        )


class DbPayment(models.Model):
    db_user = fields.ForeignKeyField("models.DbUser", related_name="payments")
    date = fields.DatetimeField()
    amount = fields.IntField()
