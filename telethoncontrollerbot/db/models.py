import datetime

from loguru import logger
from tortoise import fields, models

from telethoncontrollerbot.config.config import TZ


class Account(models.Model):
    # db_user = fields.OneToOneField("models.DbUser", related_name="db_user")
    api_id = fields.IntField()
    api_hash = fields.CharField(max_length=50)
    number = fields.CharField(max_length=20)


class DbUser(models.Model):
    user_id = fields.BigIntField(index=True)
    username = fields.CharField(max_length=255, null=True)
    subscription = fields.OneToOneField("models.Subscription", related_name="db_user")
    account = fields.OneToOneField("models.Account", related_name="db_user", null=True, on_delete=fields.SET_NULL)
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
    duration = fields.IntField(default=1)


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
    db_user = fields.OneToOneField("models.DbUser")
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
        return await cls.create(db_user=db_user, bill_id=bill_id, amount=sub_info.price, subscription=subscription)


class DbPayment(models.Model):
    db_user = fields.ForeignKeyField("models.DbUser", related_name="payments")
    date = fields.DatetimeField()
    amount = fields.IntField()


class DbTriggerCollection(models.Model):
    db_user = fields.OneToOneField("models.DbUser")
    all_message_answer = fields.TextField(null=True)
    reply_to_phrases = fields.BooleanField(default=False)
    reply_to_all = fields.BooleanField(default=False)
    reply_to_groups = fields.BooleanField(default=False)
    reply_to_channels = fields.BooleanField(default=False)

    def get_answer(self, text):
        if self.reply_to_all:
            return self.all_message_answer

        for phrase_object in self.phrase_objects:
            for phrase in phrase_object.phrases:
                if text in phrase:
                    return phrase_object.reply_to_all


class DbTrigger(models.Model):
    phrases = fields.JSONField()  # list
    answer = fields.TextField()
    trigger_collection = fields.ForeignKeyField("models.DbTriggerCollection", related_name="triggers")
