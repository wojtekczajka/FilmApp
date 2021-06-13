import fastapi as _fastapi
import models as _models
import schemas as _schemas
import shutil as _shutil
import database as _db
import sqlalchemy.orm as _orm
import typing as _typing
import os as _os
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


_models.Base.metadata.create_all(bind=_db.engine)

app = _fastapi.FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/data_stuff", StaticFiles(directory="data_stuff"), name="data")

templates = Jinja2Templates(directory="_templates")


def get_db():
    db = _db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=_fastapi.responses.HTMLResponse)
async def read_item(request: _fastapi.Request, db: _orm.Session = _fastapi.Depends(get_db)):
    # TODO def funcja do pobierania kategorii
    categories = db.query(_models.Category).all()

    #TODO def funcja do popolarnych
    popular =  db.query(_models.Film).order_by(_models.Film.rating.desc()).limit(6)
    for x in popular:
        x.film_img_url = x.film_img_url.replace("data_stuff/", "")

    # TODO def funcja do ostatnio dodanych
    latest = db.query(_models.Film).order_by(_models.Film.id.desc()).limit(6)
    for x in latest:
        x.film_img_url = x.film_img_url.replace("data_stuff/", "")

    return templates.TemplateResponse("templates-landing-page/main.html", {"request": request, "categories": categories, "popular": popular, "latest": latest})

@app.get("/{category_id}/{film_id}")


@app.get("/categories", tags=["kategorie"])
def get_categories(db: _orm.Session = _fastapi.Depends(get_db)):
    return db.query(_models.Category).all()


@app.post("/categories", response_model=_schemas.Category, tags=["dodawanie kategorii"])
def create_category(category: _schemas.CategoryCreate, db: _orm.Session = _fastapi.Depends(get_db)):
    _os.mkdir("data_stuff/" + category.name)
    new_category = _models.Category(name = category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@app.post("/categories/{category_id}/films", tags=["dodawanie filmu"])
async def create_film(category_id: int, film: _schemas.Film,  db: _orm.Session = _fastapi.Depends(get_db)):
    for instance in db.query(_models.Category).order_by(_models.Category.id):
        if(category_id == instance.id):
            _os.mkdir("data_stuff/" + instance.name + "/" + film.title)
            _os.mkdir("data_stuff/" + instance.name + "/" + film.title + "/actor-img")
            url = "data_stuff/" + instance.name + "/" + film.title + "/film-img"
    db_film = _models.Film(**film.dict(), category_id=category_id, film_img_url=url)
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    return db_film


@app.post("/{film_id}/img", tags=["dodawanie zdjec do filmu"])
async def post_img(film_id: int, images: _typing.List[_fastapi.UploadFile] = _fastapi.File(...), db: _orm.Session = _fastapi.Depends(get_db)):
    for instance in db.query(_models.Film).order_by(_models.Film.id):
        if(film_id == instance.id):
            _os.mkdir(instance.film_img_url + "/")
            path = instance.film_img_url + "/"
            img_num = 1
            for image in images:
                file_path = _os.path.relpath(path + "img" + str(img_num) + ".jpg")
                img_num += 1
                with open(file_path, "wb") as buffer:
                    _shutil.copyfileobj(image.file, buffer)


@app.post("/{film_id}/actors", tags=["dodawanie aktora"])
def create_actor(film_id: int, actor: _schemas.Actor, db: _orm.Session = _fastapi.Depends(get_db)):
    film = db.query(_models.Film).get(film_id)
    if not film:
        return{"detail": "cos jest nie tak :("}
    path =  film.film_img_url.replace("/film-img", "/actor-img")
    url = (path + "/" + actor.name + ".jpg")
    db_actor = _models.Actor(**actor.dict(), film_id = film_id, actor_img_url = url)
    db.add(db_actor)
    db.commit()
    db.refresh(db_actor)
    return db_actor


@app.post("/{film_id}/{actor_id}", tags=["dodawanie zdjec aktora"])
async def post_actor_img(film_id: int, actor_id: int, images: _typing.List[_fastapi.UploadFile] = _fastapi.File(...), db: _orm.Session = _fastapi.Depends(get_db)):

    film = db.query(_models.Film).get(film_id)
    actor = db.query(_models.Actor).get(actor_id)
    if not film:
        return{"detail": "cos jest nie tak :("}
    path = film.film_img_url.replace("/film-img", "/actor-img")
    for image in images:
        file_path = _os.path.relpath(path + "/" + actor.name + ".jpg")
        with open(file_path, "wb") as buffer:
            _shutil.copyfileobj(image.file, buffer)
    return {"detail": "Udalo sie (chyba)"}
        #data_stuff/kategoria-1/film-1-1/actor-img