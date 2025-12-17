import uuid

from sqlalchemy.orm import Mapped, mapped_column

from infrastructures.database.models.base import Base


class Notification(Base):
    id: Mapped[uuid.UUID] = mapped_column()