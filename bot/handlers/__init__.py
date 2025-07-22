from .category import router as category_router
from .user import router as user_router
from .news import router as news_router
from .ai_chat import router as ai_router

routers_list = [category_router, user_router, news_router, ai_router]
