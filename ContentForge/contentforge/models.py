"""Dataclasses reprezentujące obiekty domenowe ContentForge."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Mechanic(Enum):
    KEYWORD = "keyword"
    TREND = "trend"
    TOPIC = "topic"


class Platform(Enum):
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    BLOG = "blog"
    MEDIUM = "medium"


class PublishType(Enum):
    NOW = "now"
    SCHEDULE = "schedule"
    DRAFT = "draft"


class ContentStatus(Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class ImageSource(Enum):
    DALLE = "dalle"
    LOCAL = "local"


@dataclass
class ContentSession:
    id: Optional[int] = None
    mechanic: Mechanic = Mechanic.KEYWORD
    input_text: str = ""
    found_trend: str = ""
    language: str = "pl"
    created_at: Optional[datetime] = None


@dataclass
class GeneratedContent:
    id: Optional[int] = None
    session_id: int = 0
    platform: Platform = Platform.LINKEDIN
    title: str = ""
    body: str = ""
    hashtags: str = ""
    status: ContentStatus = ContentStatus.DRAFT
    created_at: Optional[datetime] = None


@dataclass
class ImageRecord:
    id: Optional[int] = None
    session_id: int = 0
    source: ImageSource = ImageSource.LOCAL
    file_path: str = ""
    dalle_prompt: str = ""
    postiz_id: str = ""
    postiz_path: str = ""
    created_at: Optional[datetime] = None


@dataclass
class PublishRecord:
    id: Optional[int] = None
    content_id: int = 0
    integration_id: str = ""
    integration_name: str = ""
    publish_type: PublishType = PublishType.NOW
    scheduled_at: Optional[datetime] = None
    status: str = ""
    response_data: str = ""
    created_at: Optional[datetime] = None


@dataclass
class Integration:
    id: str = ""
    name: str = ""
    provider: str = ""
    picture: str = ""
    disabled: bool = False
    cached_at: Optional[datetime] = None
