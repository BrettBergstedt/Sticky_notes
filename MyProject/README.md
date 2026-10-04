# Sticky Notes (Django)

A small Django web app for creating, viewing, editing and deleting sticky notes
(full CRUD), built with Django's Model-View-Template (MVT) architecture.

## Requirements

- Python 3.12 or newer
- Nothing else is needed. All packages are listed in `requirements.txt`.

> The virtual environment folder is **not** included (it is not portable
> between machines). Create your own with the steps below.

## Setup and run (any operating system)

Open a terminal in the project folder (the one containing `requirements.txt`).

**Windows (PowerShell or Command Prompt)**

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd sticky_notes
python manage.py migrate
python manage.py runserver
```

**macOS / Linux**

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd sticky_notes
python manage.py migrate
python manage.py runserver
```

Then open <http://127.0.0.1:8000/> in your browser. Stop the server with
`CTRL+C`.

`python manage.py migrate` builds the database (`db.sqlite3`). It is safe to
run even if `db.sqlite3` already exists.

### Optional

```
python manage.py createsuperuser   # create an admin login for /admin/
python manage.py collectstatic     # gather static files into sticky_notes/static/
```

## Running the tests

```
cd sticky_notes
python manage.py test note
```

Every test should pass and the run should end with `OK`. Django builds a
temporary test database, so your real `db.sqlite3` is never touched.

The tests cover the models, the form, every page (list, view, create, edit,
delete, including missing notes giving a 404), the URL patterns and the admin
site.

The results of the last run are saved in `test_results.txt`. To make a
fresh report, run this from the `sticky_notes` folder:

```
python make_test_report.py
```

## Pages

| URL                      | What it does                         |
| ------------------------ | ------------------------------------ |
| `/`                      | List all notes                       |
| `/note/<id>/`            | View one note                        |
| `/note/new/`             | Create a note                        |
| `/note/<id>/edit/`       | Edit a note                          |
| `/note/<id>/delete/`     | Confirm and delete a note            |
| `/admin/`                | Django admin (needs a superuser)     |

## Project layout

```
requirements.txt          Python packages (pip install -r requirements.txt)
research_answers.md       Part 1 research answers
test_results.txt          Output of the last unit test run
diagrams/                 Use case, sequence and class diagrams
sticky_notes/             Django project folder (contains manage.py)
  sticky_notes/           Project settings and main urls.py
  make_test_report.py     Runs the tests and writes test_results.txt
  note/                   The notes app
    models.py             Note and Author models
    forms.py              NoteForm
    views.py              CRUD views
    urls.py               URL patterns for the app
    tests.py              Unit tests
    migrations/           Database migrations
    templates/            base.html and note/*.html
    static/note/          styles.css
```
