from pydoc import describe

import google
from yandex_cloud_ml_sdk import AsyncYCloudML

from init.init_0 import bot_config
from init.init_1 import postgres_conn, redis_conn_users
from services.ai_chat.repositories.ai_chat.thread_storage.redis import ThreadStorageRepositoryRedis
from services.ai_chat.repositories.ai_chat.yandex_cloud import AiChatRepositoryYandexCloud
from services.ai_chat.repositories.question_lookup.yandex_cloud import QuestionLookupRepository
from services.ai_chat.repositories.questions_storage.postgres import QuestionsStorageRepositoryPostgres
from services.ai_chat.service import AiChatService
from services.events.repositories.http import EventsRepositoryHTTP
from services.events.service import EventsService
from services.rate_limiter.repositories.redis import RateLimiterRepositoryRedisFixedWindow
from services.rate_limiter.service import RateLimiterService
from utils import today_date_async, calculator_async

rate_limiter_repo_create_questions = RateLimiterRepositoryRedisFixedWindow(
    redis_conn_users,
    window_period_seconds=bot_config.RATE_LIMITER_SAVE_QUESTION_FIXED_WINDOW_SECONDS,
    max_counter_value=bot_config.RATE_LIMITER_SAVE_QUESTION_FIXED_WINDOW_MAX_COUNTER
)
rate_limiter_service_create_questions = RateLimiterService(rate_limiter_repo_create_questions, "create_questions")

events_repo = EventsRepositoryHTTP("https://api.events.sk.ru/event/list")
events_service = EventsService(events_repo)

thread_storage_repo = ThreadStorageRepositoryRedis(redis_conn_users, lambda: 24 * 3600)

# openai_client = OpenAI(api_key=bot_config.OPENAI_KEY)
# embedding_model_ru = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# question_lookup_repo = QuestionLookupRepositorySentenceTransformer(embedding_model_ru)
question_lookup_repo = QuestionLookupRepository(bot_config.YANDEX_CLOUD_FOLDER, bot_config.YANDEX_CLOUD_API_KEY)
question_storage_repo = QuestionsStorageRepositoryPostgres(postgres_conn)

yandex_ai_sdk = AsyncYCloudML(
    folder_id=bot_config.YANDEX_CLOUD_FOLDER, auth=bot_config.YANDEX_CLOUD_API_KEY
)
tools = [
    yandex_ai_sdk.tools.function(
        name="today_date",
        description="получает сегодняшнюю дату в формате YYYY-MM-DD",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        }
    ),
    yandex_ai_sdk.tools.function(
        name="events_list",
        description="получает информацию о событиях, мероприятиях сколково. если спрашивают что-то связанное с ними, "
                    "обязательно используй",
        parameters={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Дата начала периода для выборки (YYYY-MM-DD)."
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Номер страницы (начинается с 1, получить максимальное значение можно лишь из результата "
                                   "из поля pageCount)."
                },
                # "all": {
                #     "type": "integer",
                #     "enum": [1],
                #     "default": 1,
                #     "description": "Всегда должен быть равен 1."
                # }
            },
            "required": ["start_date", "page"]  # , "all"]
        },
    ),
    yandex_ai_sdk.tools.function(
        name="calculator",
        description="A simple calculator that performs basic arithmetic operations.",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate (e.g., '2 + 3 * 4').",
                }
            },
            "required": ["expression"],
        }
    )
]

model = yandex_ai_sdk.models.completions("yandexgpt", model_version="rc")
model = model.configure(
    temperature=0.3,
    # tools=tools,
    # tool_choice='required',
)

function_map = {
    "events_list": events_service.get_events_list,
    "today_date": today_date_async,
    "calculator": calculator_async,
}

ai_chat_repo = AiChatRepositoryYandexCloud(yandex_ai_sdk, model, function_map, thread_storage_repo, tools)

ai_chat_service = AiChatService(ai_chat_repo=ai_chat_repo,
                                question_lookup_repo=question_lookup_repo,
                                questions_storage_repo=question_storage_repo,
                                rate_limiter=rate_limiter_service_create_questions,
                                )
