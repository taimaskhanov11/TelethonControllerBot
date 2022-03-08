import asyncio
from typing import Optional

from pydantic import BaseModel, Field, validator, root_validator
from telethon import events

from telethoncontrollerbot.db.db_main import init_tortoise
from telethoncontrollerbot.db.models import DbTriggerCollection


class Trigger(BaseModel):
    id: int
    phrases: list[str] | str
    answer: str

    @validator("phrases")
    def get_list(cls, value):
        if isinstance(value, str):
            if value[0] == "[":
                return list(map(lambda x: x.strip(), value[1:-1].split(",")))
            return list(map(lambda x: x.strip(), value.split(",")))
        return value

    @root_validator
    def to_lower(cls, values):
        values["phrases"] = list(map(lambda x: x.lower(), values["phrases"]))
        values["answer"] = values["answer"].lower()
        return values

    def __str__(self):
        return f"➡️Фразы: {', '.join(self.phrases)}\n" f"⬅️Текст ответа: {self.answer}"


class TriggerCollection(BaseModel):
    id: int
    triggers: Optional[list[Trigger]] = Field(default_factory=list)
    reply_to_phrases: bool
    reply_to_all: bool

    reply_to_channels: bool
    reply_to_groups: bool

    all_message_answer: Optional[str]

    def get_answer(self, event: events.NewMessage.Event):
        check = True

        if event.is_channel:
            if not self.reply_to_channels:
                check = False
        elif event.is_group:
            if not self.reply_to_groups:
                check = False

        if check:
            text = event.message.text.lower()
            if self.reply_to_phrases:
                if self.triggers:
                    for phrase_object in self.triggers:
                        for phrase in phrase_object.phrases:
                            if phrase in text:
                                return phrase_object.answer

            if self.reply_to_all:
                return self.all_message_answer

    def __str__(self):
        # triggers_str = '\n\n'.join(map(str, self.triggers))
        triggers_str = ""
        for num, value in enumerate(self.triggers, 1):
            triggers_str += f"НОМЕР {num}\n{value}\n\n"
        return (
            # f"Триггеры:\n"
            f"{triggers_str}\n"
            f"Ответ на фразы: {'✅ Включен' if self.reply_to_phrases else '❌ Отключен'}\n"
            f"Ответ на любой текст сообщения: {'✅ Включен' if self.reply_to_all else '❌ Отключен'}\n"
            f"Текст ответа любой текст сообщения если включен 'Ответ на любой текст сообщения':\n"
            f"НОМЕР 0"
            f"⬅️{self.all_message_answer}\n"
            f"____________________________\n"
            f"Ответ на сообщения из групп: {'✅ Включен' if self.reply_to_groups else '❌ Отключен'}\n"
            f"Ответ на сообщения из каналов: {'✅ Включен' if self.reply_to_channels else '❌ Отключен'}\n"
        )


TRIGGERS_COLLECTION: dict[int, TriggerCollection] = {}


async def init_triggers():
    await init_tortoise()
    for colltriger in await DbTriggerCollection.all().select_related("db_user"):
        # print(dict(colltriger))
        triggers = [Trigger(**dict(tr)) for tr in await colltriger.triggers.all()]
        tc = TriggerCollection(**dict(colltriger), triggers=triggers)
        TRIGGERS_COLLECTION[colltriger.db_user.user_id] = tc
        # print(tc)
    pass


if __name__ == "__main__":
    asyncio.run(init_triggers())
