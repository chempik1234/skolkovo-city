from yandex_cloud_ml_sdk import YCloudML

from init.init_0 import bot_config
from init.init_1 import postgres_conn
from services.ai_chat.repositories.ai_chat.yandex_cloud import AiChatRepositoryYandexCloud
from services.ai_chat.repositories.question_lookup.yandex_cloud import QuestionLookupRepository
from services.ai_chat.repositories.questions_storage.postgres import QuestionsStorageRepositoryPostgres
from services.ai_chat.service import AiChatService

# openai_client = OpenAI(api_key=bot_config.OPENAI_KEY)
# embedding_model_ru = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# question_lookup_repo = QuestionLookupRepositorySentenceTransformer(embedding_model_ru)
question_lookup_repo = QuestionLookupRepository(bot_config.YANDEX_CLOUD_FOLDER, bot_config.YANDEX_CLOUD_API_KEY)
question_storage_repo = QuestionsStorageRepositoryPostgres(postgres_conn)

yandex_ai_sdk = YCloudML(
    folder_id=bot_config.YANDEX_CLOUD_FOLDER, auth=bot_config.YANDEX_CLOUD_API_KEY
)
model = yandex_ai_sdk.models.completions("yandexgpt-lite", model_version="rc")
model = model.configure(temperature=0.3)
ai_chat_repo = AiChatRepositoryYandexCloud(model)

ai_chat_service = AiChatService(ai_chat_repo=ai_chat_repo,
                                question_lookup_repo=question_lookup_repo,
                                questions_storage_repo=question_storage_repo)