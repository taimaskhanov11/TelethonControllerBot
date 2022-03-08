import asyncio
import datetime
import uuid
from typing import Optional

import aiohttp
from pydantic import BaseModel
from requests.auth import _basic_auth_str

# SHOP_ID = 878719
# YANDEX_API_KEY = "live_jGUCaplu6bfGVWGRkgK2Arvf2O3AaFqS80sv-UKZnpM"
from telethoncontrollerbot.config.config import SHOP_ID, YANDEX_API_KEY

link = "https://api.yookassa.ru/v3/payments"
headers = {"Authorization": _basic_auth_str(SHOP_ID, YANDEX_API_KEY), "Content-type": "application/json"}
tz = datetime.timezone(datetime.timedelta(hours=0))


class Confirmation(BaseModel):
    confirmation_url: str
    type: str


class Amount(BaseModel):
    currency: str
    value: float


class YooPayment(BaseModel):
    id: uuid.UUID
    amount: Amount
    description: str
    created_at: datetime.datetime
    confirmation: Optional[Confirmation]
    paid: bool
    status: str

    @classmethod
    async def create_payment(
        cls, description: str, amount: float, return_url: str = "https://t.me/MyTgControllerBot"
    ) -> "YooPayment":
        data = {
            "amount": {"value": amount, "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": description,
            # "expires_at": str(datetime.datetime.now(tz) + datetime.timedelta(minutes=15))
        }
        async with aiohttp.ClientSession(headers=headers | {"Idempotence-Key": str(uuid.uuid4())}) as session:
            async with session.post(link, json=data) as response:
                return cls.parse_obj(await response.json())

    @classmethod
    async def get(cls, bill_id: uuid.UUID) -> "YooPayment":
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"{link}/{bill_id}") as response:
                res = await response.json()
                return cls.parse_obj(res)

    @classmethod
    async def cancel(cls, bill_id: uuid.UUID) -> "YooPayment":
        async with aiohttp.ClientSession(headers=headers | {"Idempotence-Key": str(uuid.uuid4())}) as session:
            async with session.post(f"{link}/{bill_id}/cancel", json={}) as response:
                res = await response.json()
                # print(res)
                return cls.parse_obj(res)


async def main():
    yoopayment = await YooPayment.create_payment("Текстовый", 1)
    while True:
        print(await YooPayment.get(yoopayment.id))
        await asyncio.sleep(5)
        print(await YooPayment.cancel(yoopayment.id))

        # a = YooPayment.get_status(yoopayment.id)


# 29b594ab-000f-5000-9000-1e787f32f011
if __name__ == "__main__":
    # print(_basic_auth_str(SHOP_ID, YANDEX_API_KEY))
    # asyncio.run(main())
    asyncio.run(main())
