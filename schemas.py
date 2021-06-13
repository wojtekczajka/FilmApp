import typing as _typing
import pydantic as _pydantic

class FilmBase(_pydantic.BaseModel):
    title: str
    description: str



class FilmCreate(FilmBase):
    pass


class Film(_pydantic.BaseModel):
    title: str
    description: str
    title: str
    director: str
    production: int
    language: str
    rating: int

    class Config:
        orm_mode = True
        


class CategoryBase(_pydantic.BaseModel):
    name: str



class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    films: _typing.List[Film] = []

    class Config:
        orm_mode = True

class Actor(_pydantic.BaseModel):
    # id: int
    name: str
    # url: _typing.Optional[_pydantic.HttpUrl] = None
    #film_id: int

    # class Config:
    #     orm_mode = True


