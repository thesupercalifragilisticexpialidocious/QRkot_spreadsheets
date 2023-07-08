# Эмулятор благотворительной платформы

Сервис ведет учет донатов на благотворительные проекты. На платформе админы создают и редактируют проекты с определенным бюджетом. Пользователи посылают донаты (нецелевые). По мере поступления донаты распределяются между проектами в порядке очереди.

Приложение написано на фреймворке FastAPI с использованием SQLAlchemy для работы с базой данных и uvicorn для клиент-серверного взаимодействия.

# Развертывание и запуск

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:thesupercalifragilisticexpialidocious/cat_charity_fund.git
```

```
cd cat_charity_fund
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создайте файл .env c содержимым:

```
DATABASE_URL=[идентификатор СУБД в формате: mysql://username:password@server/db. опционально, по умолчанию подключится sqlite3]
SECRET=[secretforpasswordhashing]
FIRST_SUPERUSER_EMAIL=[a@a.com]
FIRST_SUPERUSER_PASSWORD=[qwertyu]

Создайте таблицы:

```
alembic upgrade head
```

Запуск:

```
uvicorn app.main:app
```

[github.com/thesupercalifragilisticexpialidocious](https://github.com/thesupercalifragilisticexpialidocious/)
email: [cmstreltsov@ya.ru](mailto:cmstreltsov@ya.ru)
