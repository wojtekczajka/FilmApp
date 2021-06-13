import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import sqlalchemy_utils as _utils
from database import Base

class Category(Base):
    __tablename__ = "categories"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String)
    items = _orm.relationship("Film", back_populates="owner")


class Film(Base):
    __tablename__ = "films"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    film_img_url = _sql.Column(_utils.URLType)
    title = _sql.Column(_sql.String)
    director = _sql.Column(_sql.String)
    production = _sql.Column(_sql.Integer)
    language = _sql.Column(_sql.String)
    rating = _sql.Column(_sql.Integer)
    description = _sql.Column(_sql.String)
    category_id = _sql.Column(_sql.Integer, _sql.ForeignKey("categories.id"))
    owner = _orm.relationship("Category", back_populates="items")
    cast = _orm.relationship("Actor", back_populates="film")


class Actor(Base):
    __tablename__ = "actors"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String)
    actor_img_url = _sql.Column(_utils.URLType)
    film_id = _sql.Column(_sql.Integer, _sql.ForeignKey("films.id"))
    film = _orm.relationship("Film", back_populates="cast")
