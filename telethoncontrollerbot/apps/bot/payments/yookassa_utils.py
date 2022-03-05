import datetime
import time
import uuid
from typing import Optional

from pydantic import BaseModel
from yookassa import Configuration, Payment

SHOP_ID = 878719
YANDEX_API_KEY = "live_jGUCaplu6bfGVWGRkgK2Arvf2O3AaFqS80sv-UKZnpM"
Configuration.configure(SHOP_ID, YANDEX_API_KEY)


def create_payment():
    payment_id = uuid.uuid4()
    payment = Payment.create({
        "amount": {
            "value": "1",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.merchant-website.com/return_url"
        },
        "capture": True,
        "description": "Заказ №1"
    }, payment_id)
    # return YooPayment.parse_obj()
    print(payment.status)
    print(payment.id)
    print(dict(payment))
    print(str(payment_id))
    while True:
        time.sleep(2)
        try:
            print(dict(Payment.find_one(payment.id)))  # succeeded
            print(YooPayment.parse_obj(Payment.find_one(payment.id)))
        except Exception as e:
            print(e)
            pass


# payment_id = "29b586b0-000f-5000-9000-188c0ca93848"
# print(dict(Payment.find_one(payment_id)))
payment_id = '29b585c1-000f-5000-9000-136050bf7b9f'
idempotence_key = str(uuid.uuid4())
if __name__ == '__main__':
    # pass
    # create_payment()

    print(dict(Payment.cancel(payment_id, idempotence_key)))