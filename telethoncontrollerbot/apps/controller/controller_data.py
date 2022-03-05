from pydantic import BaseModel


class PhraseObject(BaseModel):
    phrases: list[str]
    answer: str


class Trigger(BaseModel):
    phrase_objects: list[PhraseObject]

    all_message_answer: str
    all_message: bool

    def get_answer(self, text):
        if self.all_message:
            return self.all_message_answer

        for phrase_object in self.phrase_objects:
            for phrase in phrase_object.phrases:
                if text in phrase:
                    return phrase_object.answer

USERS_TRIGGERS: dict[str] = {}
