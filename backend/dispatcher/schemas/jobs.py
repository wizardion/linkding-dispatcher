from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str = Field(serialization_alias="id")
    job_try: int = Field(serialization_alias="jobTry")
    function: str = Field(serialization_alias="name")
    start_time: datetime = Field(serialization_alias="start")
    finish_time: datetime = Field(serialization_alias="finish")
    enqueue_time: datetime = Field(serialization_alias="enqueued")
    result: bool = Field(serialization_alias="success")
