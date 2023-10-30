from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse 
from fastapi.templating import Jinja2Templates
from typing import Annotated
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
    c.execute('SELECT COUNT(*) FROM todos')
    total = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM todos WHERE done')
    done = c.fetchone()[0]
    count = {'done': done, 'total': total}
    return template.TemplateResponse('index.html', {'request': request, 'todos': todos, 'count': count})

@app.post('/add')
async def add(title: Annotated[str, Form()]):
    if title:
        c.execute('INSERT INTO todos (title, done) VALUES (?, 0)', (title, ))
        conn.commit()

    return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)

@app.delete('/delete/{id}')
async def delete(id):
    c.execute('DELETE FROM todos WHERE id=?', (id,))
    conn.commit()
    return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)

@app.put('/update/{id}')
async def update(id):
    todo = c.execute('SELECT done FROM todos WHERE id=?', (id,)).fetchone()[0]
    if todo is 0:
        c.execute('UPDATE todos SET done=true WHERE id=?', (id,))
    else:
        c.execute('UPDATE todos SET done=false WHERE id=?', (id,))
    conn.commit()
    return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
