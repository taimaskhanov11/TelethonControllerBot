import asyncio

from pydantic import BaseModel, validator, root_validator

from telethoncontrollerbot.db.db_main import init_tortoise
from telethoncontrollerbot.db.models import DbTriggerCollection


class Trigger(BaseModel):
    phrases: list[str] | str
    answer: str

    @validator("phrases")
    def get_list(cls, value):
        if isinstance(value, str):
            if value[0] == "[":
                return value[1:-1].split(", ")
            return value.split(", ")
        return value

    @root_validator
    def to_lower(cls, values):
        values["phrases"] = list(map(lambda x: x.lower(), values["phrases"]))
        values["answer"] = values["answer"].lower()
        return values

    def __str__(self):
        return (
            f"➡️Фразы: {', '.join(self.phrases)}\n"
            f"⬅️Текст ответа: {self.answer}"
        )


class TriggerCollection(BaseModel):
    triggers: list[Trigger]
    all_message_answer: str
    reply_to_all: bool

    def get_answer(self, text: str):
        text = text.lower()
        if self.reply_to_all:
            return self.all_message_answer

        for phrase_object in self.triggers:
            for phrase in phrase_object.phrases:
                if text in phrase:
                    return phrase_object.answer

    def __str__(self):
        # triggers_str = '\n\n'.join(map(str, self.triggers))
        triggers_str = ""
        for num, value in enumerate(self.triggers, 1):
            triggers_str += f"{num}\n{value}\n\n"

        return (
            # f"Триггеры:\n"
            f"{triggers_str}\n"
            f"Ответ на все сообщения: {'✅ Включен' if self.reply_to_all else '❌ Отключен'}\n"
            f"Текст ответа на все сообщения:{self.all_message_answer}"
        )


USERS_TRIGGERS_COLLECTION: dict[int, TriggerCollection] = {}


async def init_triggers():
    await init_tortoise()
    for colltriger in await DbTriggerCollection.all().select_related("db_user"):
        # print(dict(colltriger))
        triggers = [Trigger(**dict(tr)) for tr in await colltriger.triggers.all()]
        tc = TriggerCollection(**dict(colltriger), triggers=triggers)
        USERS_TRIGGERS_COLLECTION[colltriger.db_user.user_id] = tc

    pass


if __name__ == '__main__':
    asyncio.run(init_triggers())
