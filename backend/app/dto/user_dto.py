from pydantic import BaseModel, ConfigDict

class UserDto(BaseModel):
    model_config = ConfigDict(from_attributes=True) #directly map the attributes of the model to the dto

    id: int
    email: str
    display_name: str
    role: str