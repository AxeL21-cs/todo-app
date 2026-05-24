"""Notification router handling CRUD operations and reminder detection."""

import os

from fastapi import APIRouter, Depends, Response

from dependencies import get_current_user
from exceptions import NotFoundError
from models import (
    Notification,
    NotificationResponse,
    NotificationsListResponse,
    User,
)
from services.notification_service import NotificationService
from services.reminder_checker import check_user
from store import JSONStore

# Initialize stores and services
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
notification_store = JSONStore(os.path.join(DATA_DIR, "notifications.json"))
todo_store = JSONStore(os.path.join(DATA_DIR, "todos.json"))
notification_service = NotificationService(notification_store)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=NotificationsListResponse)
async def list_notifications(
    current_user: User = Depends(get_current_user),
) -> NotificationsListResponse:
    """Get notifications for the authenticated user.

    On each poll, this endpoint:
    1. Reads the user's todos from todo_store
    2. Reads existing notifications from notification_store
    3. Calls reminder_checker.check_user() to detect new due notifications
    4. Creates any newly detected notifications
    5. Returns the full notification list + unread_count

    Args:
        current_user: The authenticated user (injected by dependency).

    Returns:
        NotificationsListResponse with notifications array and unread_count.
    """
    # Read user's todos
    all_todos = todo_store.read_all()
    user_todos = [t for t in all_todos if t.get("user_id") == current_user.id]

    # Read existing notifications for this user
    existing_notifications = notification_service.get_user_notifications_raw(current_user.id)

    # Detect new notifications using reminder_checker
    new_notifications = check_user(
        user_id=current_user.id,
        todos=user_todos,
        existing_notifications=existing_notifications,
    )

    # Create any newly detected notifications
    for todo_id, notification_type, message in new_notifications:
        notification_service.create(
            user_id=current_user.id,
            todo_id=todo_id,
            notification_type=notification_type,
            message=message,
        )

    # Return the full list
    notifications = notification_service.list_for_user(current_user.id)
    unread_count = notification_service.get_unread_count(current_user.id)

    return NotificationsListResponse(
        notifications=[
            NotificationResponse(
                id=n.id,
                user_id=n.user_id,
                todo_id=n.todo_id,
                type=n.type.value,
                message=n.message,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            for n in notifications
        ],
        unread_count=unread_count,
    )


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
) -> NotificationResponse:
    """Mark a single notification as read.

    Args:
        notification_id: The notification's ID to mark as read.
        current_user: The authenticated user (injected by dependency).

    Returns:
        The updated notification.

    Raises:
        NotFoundError: If notification is not found or not owned by user.
    """
    notification = notification_service.mark_as_read(
        user_id=current_user.id,
        notification_id=notification_id,
    )

    if not notification:
        raise NotFoundError("Notification not found")

    return NotificationResponse(
        id=notification.id,
        user_id=notification.user_id,
        todo_id=notification.todo_id,
        type=notification.type.value,
        message=notification.message,
        is_read=notification.is_read,
        created_at=notification.created_at,
    )


@router.post("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Mark all notifications as read for the authenticated user.

    Args:
        current_user: The authenticated user (injected by dependency).

    Returns:
        Dict with marked_count indicating how many were marked.
    """
    marked_count = notification_service.mark_all_as_read(current_user.id)
    return {"marked_count": marked_count}


@router.delete("", status_code=204)
async def clear_all_notifications(
    current_user: User = Depends(get_current_user),
) -> Response:
    """Clear all notifications for the authenticated user.

    Args:
        current_user: The authenticated user (injected by dependency).

    Returns:
        204 No Content response on success.
    """
    notification_service.clear_all(current_user.id)
    return Response(status_code=204)
