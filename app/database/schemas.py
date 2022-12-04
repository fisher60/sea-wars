from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class PlayerBase(BaseModel):
    pass


class PlayerCreate(PlayerBase):
    user_id: int


class Player(PlayerBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class User(UserBase):
    id: int
    player: Player

    class Config:
        orm_mode = True
