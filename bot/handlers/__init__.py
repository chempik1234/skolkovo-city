from .category import router as category_router
from .user import router as user_router
from .news import router as news_router

routers_list = [category_router, user_router, news_router]
