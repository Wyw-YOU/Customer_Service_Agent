from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, ConversationMessage
from app.models.user import User


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_conversations(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        q = (
            select(Conversation, User)
            .join(User, Conversation.user_id == User.id)
            .order_by(Conversation.updated_at.desc(), Conversation.created_at.desc())
            .offset(offset)
            .limit(limit)
            .options(selectinload(Conversation.messages))
        )
        if status:
            q = q.where(Conversation.status == status)

        result = await self.session.execute(q)
        return [
            self._conversation_summary(conversation, user)
            for conversation, user in result.all()
        ]

    async def get_conversation_detail(self, conversation_id: int) -> dict | None:
        q = (
            select(Conversation, User)
            .join(User, Conversation.user_id == User.id)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        result = await self.session.execute(q)
        row = result.one_or_none()
        if row is None:
            return None

        conversation, user = row
        detail = self._conversation_summary(conversation, user)
        detail["messages"] = [
            self._message_to_dict(message)
            for message in sorted(
                conversation.messages,
                key=lambda item: (item.timestamp is None, item.timestamp, item.id),
            )
        ]
        return detail

    async def list_users(
        self,
        role: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        q = select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
        if role:
            q = q.where(User.role == role)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    def _conversation_summary(self, conversation: Conversation, user: User) -> dict:
        messages = sorted(
            conversation.messages,
            key=lambda item: (item.timestamp is None, item.timestamp, item.id),
        )
        last_message = messages[-1] if messages else None
        return {
            "id": conversation.id,
            "user_id": user.id,
            "username": user.username,
            "user_email": user.email,
            "user_phone": user.phone,
            "title": conversation.title,
            "status": conversation.status,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "last_message_at": last_message.timestamp if last_message else None,
            "last_message_role": last_message.role if last_message else None,
            "last_message_preview": self._preview(last_message.content) if last_message else None,
            "message_count": len(messages),
        }

    def _message_to_dict(self, message: ConversationMessage) -> dict:
        return {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "role": message.role,
            "content": message.content,
            "sources": message.sources,
            "timestamp": message.timestamp,
        }

    def _preview(self, content: str, limit: int = 80) -> str:
        value = " ".join(content.split())
        if len(value) <= limit:
            return value
        return f"{value[:limit]}..."
