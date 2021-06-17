import fastapi as _fastapi
import models as _models
import database as _db
import sqlalchemy.orm as _orm
import random


def get_db():
    db = _db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def append_popular_films(popular: _models.Film, db: _orm.Session = _fastapi.Depends(get_db)):
    pop_hrefs = []
    for x in popular:
        x.film_img_url = x.film_img_url.replace("data_stuff/", "")
        title = db.query(_models.Category).filter(_models.Category.id == x.category_id).first()
        pop_hrefs.append(title.name + "/" + x.title)
    return pop_hrefs


def append_latest_film(latest: _models.Film, db: _orm.Session = _fastapi.Depends(get_db)):
    latest_hrefs = []
    for x in latest:
        x.film_img_url = x.film_img_url.replace("data_stuff/", "")
        title = db.query(_models.Category).filter(_models.Category.id == x.category_id).first()
        latest_hrefs.append(title.name + "/" + x.title)


def random_movie_url(db: _orm.Session = _fastapi.Depends(get_db)):
    categories = db.query(_models.Category).all()
    if not categories:
        return None
    rand_cat = random.choice(categories)
    films = db.query(_models.Film).filter(_models.Film.category_id == rand_cat.id).all()
    if not films:
        return None
    rand_film = random.choice(films)
    url = "/" + rand_cat.name + "/" + rand_film.title + "/"
    print(url)
    return url


def replace_url(category_name: str, film_name: str):
    category_name.replace("+", " ")
    film_name.replace("+", " ")


def append_img_hrefs(film: _models.Film):
    films_img_hrefs = []
    film.film_img_url = film.film_img_url.replace("data_stuff/", "")
    for i in range(1, 4):
        films_img_hrefs.append(film.film_img_url + "/img" + str(i) + ".jpg")
    return films_img_hrefs


def replace_actors_url(actors: _models.Actor):
    for actor in actors:
        actor.actor_img_url = actor.actor_img_url.replace("data_stuff/", "")


def get_cat(category_name: str, db: _orm.Session = _fastapi.Depends(get_db)):
    cat = db.query(_models.Category).filter(_models.Category.name == category_name).first()
    if not cat:
        return None
    return cat
