from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


class Voice(BaseModel):
    name: str
    language_code: str = Field(alias="lang")

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class VoiceAttend(Voice):
    hashed_id: str


voice = Voice(name="Filiz", lang="tr-TR")
voice_dict = voice.model_dump()
voice_dict["hashedId"] = "1"
voice_attend = VoiceAttend.model_validate(voice_dict)
print(voice_attend.model_dump())
print(voice.language_code)
# > tr-TR
print(voice.model_dump(by_alias=True))
# > {'Name': 'Filiz', 'lang': 'tr-TR'}
