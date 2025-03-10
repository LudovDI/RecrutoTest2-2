import os

import uvicorn as uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
import random

app = FastAPI()

# Фейковые пользователи для примера
dummy_users = {"user": "1111"}
sessions = {}


def authenticate_user(username: str, password: str):
    return dummy_users.get(username) == password


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if authenticate_user(form_data.username, form_data.password):
        token = str(random.randint(100000, 999999))  # Простая сессия
        sessions[token] = form_data.username
        response = RedirectResponse(url=f"/?token={token}", status_code=status.HTTP_303_SEE_OTHER)
        return response
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )


def generate_code():
    return str(random.randint(1000, 9999))


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    token = request.query_params.get("token")
    if not token or token not in sessions:
        return RedirectResponse(url="/login")

    code = generate_code()
    del sessions[token]  # Удаляем сессию после загрузки страницы
    html_content = f"""
    <html>
        <head>
            <title>Random Code Generator</title>
        </head>
        <body>
            <h1>Ваш случайный код: {code}</h1>
            <p>После обновления страницы вам нужно снова войти.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/login", response_class=HTMLResponse)
def login_page():
    return HTMLResponse("""
    <html>
        <head><title>Login</title></head>
        <body>
            <form action='/token' method='post'>
                <input type='text' name='username' placeholder='Username' required>
                <input type='password' name='password' placeholder='Password' required>
                <button type='submit'>Login</button>
            </form>
        </body>
    </html>
    """)


# Запуск сервера (добавлено в конец файла)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Используем порт из переменной окружения
    uvicorn.run(app, host="0.0.0.0", port=port)
