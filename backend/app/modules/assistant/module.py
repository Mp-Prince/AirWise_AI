"""AI Assistant API module (Phase 5)."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.modules.assistant.schema import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantFeedbackRequest,
    AssistantFeedbackResponse,
)
from app.modules.assistant.service import AssistantService, RateLimitExceededError
from app.modules.chat_conversations.schema import (
    ChatMessageSchema,
    ConversationDetail,
    ConversationListResponse,
    ConversationSummary,
)
from app.modules.chat_conversations.service import ChatConversationService
from app.modules.chat_messages.service import ChatMessageService
from app.modules.users.models import UserModel
from app.modules.users.routes import get_current_active_user

router = APIRouter(tags=["assistant"])


@router.post("/chat", response_model=AssistantChatResponse)
async def chat_with_assistant(
    request: AssistantChatRequest,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Send a message to the grounded AI assistant."""
    service = AssistantService(session)
    try:
        response = await service.chat(current_user.id, request)
        await session.commit()
        return response
    except RateLimitExceededError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """List the signed-in user's conversations."""
    conv_service = ChatConversationService(session)
    convs = await conv_service.list_for_user(current_user.id)
    return ConversationListResponse(
        conversations=[ConversationSummary.model_validate(c) for c in convs],
        total=len(convs),
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Get a conversation and its message history (owner only)."""
    conv_service = ChatConversationService(session)
    conv = await conv_service.get_for_user(conversation_id, current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_service = ChatMessageService(session)
    messages = await msg_service.get_history(conv.id)
    return ConversationDetail(
        **ConversationSummary.model_validate(conv).model_dump(),
        messages=[ChatMessageSchema.model_validate(m) for m in messages],
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Delete a conversation belonging to the current user."""
    conv_service = ChatConversationService(session)
    deleted = await conv_service.delete_for_user(conversation_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await session.commit()


@router.post("/feedback", response_model=AssistantFeedbackResponse)
async def submit_feedback(
    request: AssistantFeedbackRequest,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Record helpful/not-helpful feedback for an assistant message."""
    service = AssistantService(session)
    await service.record_feedback(
        user_id=current_user.id,
        message_id=request.message_id,
        helpful=request.helpful,
        comment=request.comment,
    )
    await session.commit()
    return AssistantFeedbackResponse(status="recorded", message_id=request.message_id)


@router.get("/usage", response_model=dict)
async def get_assistant_usage(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Return rate-limit and token/cost usage summary for the current user."""
    service = AssistantService(session)
    return service.get_user_usage(current_user.id)
