# Сервис кастомных нотификаций через Telegram

## Описание проекта

Сервис предназначен для отправки кастомных уведомлений через Telegram с гарантией доставки exactly once. Система обеспечивает надежную доставку сообщений, обработку ошибок и возможность повторных попыток отправки.

## Архитектура системы

### Компоненты системы

1. **API Gateway (FastAPI)**
   - REST API для управления задачами
   - Аутентификация и авторизация (JWT)
   - Валидация входящих данных
   - Маршрутизация запросов

2. **База данных (PostgreSQL)**
   - Хранение задач (в перспективе их статусов)
   - Отслеживание доставки сообщений
   - Аудит операций
   - Масштабируемость и репликация

3. ***Task Broker (TaskIQ) (не реализовано)***
   - Очередь задач для асинхронной обработки
   - Гарантированная доставка сообщений
   - Механизм повторных попыток
   - Мониторинг состояния задач

4. ***Message Sender (Aiogram) (не реализовано)***
   - Отправка сообщений в Telegram
   - Обработка ответов от Telegram API
   - Логирование результатов отправки
   - Обработка ошибок сети



### Схема взаимодействия

```
                 +------------------+
                 |     Клиент       |
                 +--------+---------+
                          |
                          | HTTP запрос (CRUD)
                          v
                 +--------+---------+
                 |   API Gateway    |
                 |   (FastAPI)      |
                 +--------+---------+
                          |
        +-----------------+-----------------+
        |                                   |
        | Запись задачи в БД                | JWT аутентификация
        v                                   |
 +------+--------+                          |
 |   PostgreSQL  |<-------------------------+
 | (хранение и   |
 |  статус задач)|                         
 +------+--------+                         
        |                                       
        | Добавление задачи в очередь (будущее)
        v                                       
 +------+--------+                              
 |   Task Broker |                             
 |   (TaskIQ)    |                             
 +------+--------+                              
        |                                       
        | Извлечение задачи                     
        v                                       
 +------+--------+                              
 | Message Sender|                              
 |  (Aiogram)    |                             
 +------+--------+                              
        |                                       
        | Telegram API запрос                  
        v                                       
 +------+--------+                              
 | Telegram Bot  |                              
 +---------------+                              

```

## Механизм работы

1. **Создание задачи**
   - Клиент отправляет запрос на создание задачи через API
   - API Gateway валидирует данные и создает запись в БД
   - Задача добавляется в очередь TaskIQ
   - Возвращается ID задачи клиенту

2. **Обработка задачи**
   - TaskIQ извлекает задачу из очереди
   - Проверяется статус задачи в БД
   - Если задача не обработана, она передается в Message Sender
   - Message Sender отправляет сообщение через Aiogram

## Интеграция TaskIQ и Aiogram

### TaskIQ Integration

```python
# app/tasks/notification.py
from taskiq import TaskiqMessage, TaskiqState
from app.services.telegram import TelegramService

async def send_notification(
    message: TaskiqMessage,
    state: TaskiqState,
    telegram_service: TelegramService
) -> None:
    """
    TaskIQ задача для отправки уведомления.
    
    Args:
        message: Сообщение из очереди
        state: Состояние задачи
        telegram_service: Сервис для работы с Telegram
    """
    task_id = message.task_id
    try:
        # Получение данных задачи из БД
        task = await get_task(task_id)
        
        # Отправка сообщения
        result = await telegram_service.send_message(
            chat_id=task.chat_id,
            text=task.message
        )
        
        # Обновление статуса
        await update_task_status(task_id, "delivered")
        
    except Exception as e:
        # Обработка ошибок и повторная попытка
        await handle_delivery_error(task_id, e)
        raise
```

### Aiogram Integration

```python
# app/services/telegram.py
from aiogram import Bot
from app.infrastructure.config import settings

class TelegramService:
    """
    Сервис для работы с Telegram API.
    """
    def __init__(self):
        self.bot = Bot(token=settings.telegram.bot_token)
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        **kwargs
    ) -> dict:
        """
        Отправка сообщения в Telegram.
        
        Args:
            chat_id: ID чата
            text: Текст сообщения
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Результат отправки
        """
        try:
            result = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                **kwargs
            )
            return {
                "message_id": result.message_id,
                "status": "sent"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
```

## Сильные стороны

1. **Надежность**
   - Гарантированная доставка сообщений
   - Сохранение состояния задачи в БД

2. **Масштабируемость**
   - Асинхронная обработка задач
   - Возможность горизонтального масштабирования
   - Разделение ответственности компонентов

3. **Безопасность**
   - JWT аутентификация
   - Валидация данных

## Слабые стороны

1. **Ресурсоемкость**
   - Требования к БД
   - Хранение истории задач в БД
   - Отсутствие кеширования
2. **Мониторинг**
   - Отсутствие логирования

## Технологический стек

- **Backend**: Python 3.11+
- **API Framework**: FastAPI
- **Task Broker**: TaskIQ
- **Telegram Bot**: Aiogram 3.x
- **Database**: PostgreSQL
- **Authentication**: JWT
- **Testing**: pytest
- **Documentation**: OpenAPI/Swagger

## Установка и запуск

1. Клонировать репозиторий
2. Настроить переменные окружения в `.env`
3. Запустить docker-compose.yaml
4. Запустить миграции: `alembic upgrade head`

## API Endpoints

- `POST /api/tasks/create` - Создание задачи
- `GET /api/tasks/{task_id}` - Получение информации о задачи
- `GET /api/tasks/list` - Список задач
- `PATCH /api/tasks/{task_id}/update` - Обновление задачи
- `DELETE /api/tasks/{task_id}` - Удаление задачи
