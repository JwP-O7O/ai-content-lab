from enum import Enum

class ContentFormat(Enum):
    SINGLE_TWEET = "tweet"
    THREAD = "thread"
    TELEGRAM_MESSAGE = "telegram"
    BLOG_POST = "blog"
    IMAGE_POST = "image"

class ContentPlan:
    def __init__(self):
        self.id = 1
        self.status = "pending"
        self.format = ContentFormat.SINGLE_TWEET

class AgentLog:
    def __init__(self, **kwargs): pass
