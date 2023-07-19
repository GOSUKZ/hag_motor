# FastAPI with asynchronous Python driver for MongoDB (Motor asyncio)

## Requirements
+ Python 3.7+
+ FastAPI
+ Motor (for async MongoDB operations)
+ Pydantic (for data validation)
+ Uvicorn (ASGI server)
+ MongoDB (Make sure you have MongoDB installed and running locally or provide a remote connection URL)

## Installation
+ Clone the repository
+ Create a virtual environment (optional but recommended)
+ Install the required dependencies: `pip install -r requirements.txt`
+ Set Environment Variables `env.exemple.txt`

## Usage
+ Run the FastAPI application using Uvicorn:
  - run the file `/main.py` in debug mode
  - or make changes to the files `/main.py`, `app/__init__.py`, `app/internal/config.py` following the instructions from the comments after which the project is launched from `/main.py`

## MongoDB Connection
The application uses motor_asyncio to connect asynchronously to a MongoDB database. The connection URL is read from the `MONGODB_URL` environment variable. The connection is established in the app object's startup event and closed in the shutdown event.

## API Documentation
Visit `http://localhost:8000/docs` to access the Swagger UI and interact with the API. You can test the endpoints and view the API documentation.

## Disclaimer
This is a sample FastAPI application meant for educational purposes. It may not be suitable for production use as-is. Make sure to follow best practices and security measures when deploying a real-world application.
Please update the README.md with relevant information specific to your project, including detailed API documentation, additional endpoints, usage instructions, and any other important details.

# FastAPI с асинхронным драйвером Python для MongoDB (Motor asyncio) 

## Требования 
+ Python 3.7+
+ FastAPI
+ Motor (для асинхронных операций MongoDB)
+ Pydantic (для проверки данных)
+ Uvicorn (сервер ASGI)
+ MongoDB (убедитесь, что MongoDB установлена ​​и работает локально, или укажите URL-адрес удаленного подключения)

## Монтаж 
+ Клонировать репозиторий
+ Создайте виртуальную среду (необязательно, но рекомендуется)
+ Установите необходимые зависимости: `pip install -r requirements.txt`
+ Установить переменные среды `env.exemple.txt`

## Применение 
+ Запустите приложение FastAPI с помощью Uvicorn:
   - запустить файл `/main.py` в режиме отладки
   - или внести изменения в файлы `/main.py`, `app/__init__.py`, `app/internal/config.py` следуя инструкциям из комментариев, после чего проект запускается из `/main.py`

## Соединение с MongoDB 
Приложение использует motor_asyncio для асинхронного подключения к базе данных MongoDB. URL-адрес подключения считывается из переменной среды `MONGODB_URL`. Соединение устанавливается в событии запуска объекта приложения и закрывается в событии выключения. 

## Документация API 
Посетите `http://localhost:8000/docs`, чтобы получить доступ к пользовательскому интерфейсу Swagger и взаимодействовать с API. Вы можете протестировать конечные точки и просмотреть документацию по API. 

## Отказ от ответственности 
Это пример приложения FastAPI, предназначенного для образовательных целей. Он может не подходить для производственного использования в том виде, в каком он есть. Обязательно следуйте передовым методам и мерам безопасности при развертывании реального приложения. Пожалуйста, обновите README.md с соответствующей информацией, относящейся к вашему проекту, включая подробную документацию по API, дополнительные конечные точки, инструкции по использованию и любые другие важные детали.
