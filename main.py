from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse 
from starlette.responses import FileResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import tempfile
from pathlib import Path 

app = FastAPI()

template = Jinja2Templates(directory='.')

# create a database in a temporary directory
db_path = Path(tempfile.gettempdir()) / 'htmx_todo.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute(
    'CREATE TABLE IF NOT EXISTS todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done BOOL NOT NULL)'
)
conn.commit()


@app.get('/', response_class=HTMLResponse)
async def get(request: Request):
    todos = c.execute('SELECT * FROM todos ORDER BY id').fetchall()
    c.execute("SELECT COUNT(*) FROM todos")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM todos WHERE done")
    done = c.fetchone()[0]
    count = {'done': done, 'total': total}
    return template.TemplateResponse('index.html', {'request': request, 'todos': todos, 'count': count})
