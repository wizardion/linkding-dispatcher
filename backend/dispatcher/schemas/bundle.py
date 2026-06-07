from pydantic import BaseModel, ConfigDict, SerializationInfo, model_serializer


class Bundle(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    all_tags: str
    order: int

    @model_serializer(mode="wrap")
    def serialize_model(self, handler, info: SerializationInfo):
        if not info.by_alias:
            return handler(self)

        return {
            "name": self.name,
            "tag": self.all_tags,
        }
