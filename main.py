import fastapi as _fastapi
import crud as _crud
import models as _models
import schemas as _schemas
import shutil as _shutil
import database as _db
import sqlalchemy.orm as _orm
import typing as _typing
import os as _os
from starlette.responses import RedirectResponse
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



@app.get("/", response_class=_fastapi.responses.HTMLResponse, tags=["landing-page"])
async def read_item(request: _fastapi.Request, db: _orm.Session = _fastapi.Depends(get_db)):

    categories = db.query(_models.Category).all()
    popular =  db.query(_models.Film).order_by(_models.Film.rating.desc()).limit(6)
    latest = db.query(_models.Film).order_by(_models.Film.id.desc()).limit(6)

    latest_hrefs = []
    for x in latest:
        x.film_img_url = x.film_img_url.replace("data_stuff/", "")
        title = db.query(_models.Category).filter(_models.Category.id == x.category_id).first()
        latest_hrefs.append(title.name + "/" + x.title)

    pop_hrefs = _crud.append_popular_films(popular, db)
    return templates.TemplateResponse("templates-landing-page/main.html", {"request": request, "categories": categories,
                                                                           "popular": popular, "pop_href": pop_hrefs,
                                                                           "latest_href": latest_hrefs, "latest": latest})


@app.get("/rand", tags=["rand"])
async def rand(db: _orm.Session = _fastapi.Depends(get_db)):
    url = _crud.random_movie_url(db)
    if not url:
        return {"detail": "movie is not available"}
    redirect = RedirectResponse(url=url, headers={'Authorization': "some_long_key"})
    if not redirect:
        return {"detail": "smth went wrong with redirect"}
    return redirect

@app.get("/{category_name}/{film_name}", response_class=_fastapi.responses.HTMLResponse, tags = ["film-page"])
async def rand(request: _fastapi.Request, category_name: str, film_name: str, db: _orm.Session = _fastapi.Depends(get_db)):
    category_name = category_name.replace("+", " ")
    film_name = film_name.replace("+", " ")
    categories = db.query(_models.Category).all()
    film = db.query(_models.Film).filter(_models.Film.title == film_name).first()
    actors = db.query(_models.Actor).filter(_models.Actor.film_id == film.id).limit(6)

    if not film:
        raise _fastapi.HTTPException(status_code=404, detail="Item not found")

    films_img_hrefs = _crud.append_img_hrefs(film)
    _crud.replace_actors_url(actors)

    return templates.TemplateResponse("templates-film-page/film_page.html", {"request": request, "categories": categories, "film": film, "category_name": category_name, "img_href": films_img_hrefs, "actors": actors})



@app.get("/{category_name}", response_class= _fastapi.responses.HTMLResponse, tags=["category-list-page"])
async def get_categories_list(request: _fastapi.Request, category_name: str, db: _orm.Session = _fastapi.Depends(get_db)):

    cat = _crud.get_cat(category_name, db)
    if not cat:
        raise _fastapi.HTTPException(status_code=404, detail="Category not found :(")
    
    categories = db.query(_models.Category).all()

    films_list = db.query(_models.Film).filter(_models.Film.category_id == cat.id).all()

    return templates.TemplateResponse("categories-page/categories.html", {"request": request, "categories": categories, "film_list": films_list, "category_name": category_name})


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