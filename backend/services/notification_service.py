"""Notification service handling CRUD operations for user notifications."""

import uuid
from datetime import datetime, timezone

from models import Notification, NotificationType
from store import JSONStore


class NotificationService:
    """Handles CRUD operations on notifications scoped to the authenticated user."""

    def __init__(self, notification_store: JSONStore):
        """Initialize with notification store.

        Args:
            notification_store: JSONStore instance for notification persistence.
        """
        self.notification_store = notification_store

    def create(self, user_id: str, todo_id: str, notification_type: str, message: str) -> Notification:
        """Create a new notification.

        Args:
            user_id: UUID4 string of the notification owner.
            todo_id: UUID4 string of the related todo.
            notification_type: "reminder" or "overdue".
            message: Human-readable notification message.

        Returns:
            Notification Pydantic model instance.

        Side Effects:
            Persists to notifications.json via JSONStore.
        """
        notification_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "todo_id": todo_id,
            "type": notification_type,
            "message": message,
            "is_read": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self.notification_store.add(notification_data)

        return Notification(**notification_data)

    def exists(self, user_id: str, todo_id: str, notification_type: str) -> bool:
        """Check if a notification already exists for deduplication.

        Args:
            user_id: UUID4 string of the notification owner.
            todo_id: UUID4 string of the related todo.
            notification_type: "reminder" or "overdue".

        Returns:
            True if a notification with this (user_id, todo_id, type) exists.
        """
        all_records = self.notification_store.read_all()
        for record in all_records:
            if (
                record.get("user_id") == user_id
                and record.get("todo_id") == todo_id
                and record.get("type") == notification_type
            ):
                return True
        return False

    def list_for_user(self, user_id: str) -> list[Notification]:
        """List notifications for a user, ordered by created_at DESC, max 20.

        Args:
            user_id: UUID4 string of the user.

        Returns:
            List of Notification objects, most recent first, capped at 20.
        """
        all_records = self.notification_store.read_all()
        user_notifications = [r for r in all_records if r.get("user_id") == user_id]

        # Sort by created_at descending
        user_notifications.sort(key=lambda r: r.get("created_at", ""), reverse=True)

        # Cap at 20
        user_notifications = user_notifications[:20]

        return [Notification(**r) for r in user_notifications]

    def get_unread_count(self, user_id: str) -> int:
        """Get the total number of unread notifications for a user.

        Args:
            user_id: UUID4 string of the user.

        Returns:
            Integer count of unread notifications.
        """
        all_records = self.notification_store.read_all()
        return sum(
            1
            for r in all_records
            if r.get("user_id") == user_id and not r.get("is_read", False)
        )

    def mark_as_read(self, user_id: str, notification_id: str) -> Notification | None:
        """Mark a single notification as read.

        Args:
            user_id: UUID4 string of the user (for ownership check).
            notification_id: UUID4 string of the notification to mark.

        Returns:
            The updated Notification, or None if not found/not owned.
        """
        record = self.notification_store.find_by_id(notification_id)

        if not record or record.get("user_id") != user_id:
            return None

        updated = self.notification_store.update(notification_id, {"is_read": True})
        if not updated:
            return None

        return Notification(**updated)

    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications for a user as read.

        Args:
            user_id: UUID4 string of the user.

        Returns:
            Number of notifications that were marked as read.
        """
        all_records = self.notification_store.read_all()
        marked_count = 0

        for record in all_records:
            if record.get("user_id") == user_id and not record.get("is_read", False):
                record["is_read"] = True
                marked_count += 1

        if marked_count > 0:
            self.notification_store.write_all(all_records)

        return marked_count

    def clear_all(self, user_id: str) -> None:
        """Delete all notifications for a user.

        Args:
            user_id: UUID4 string of the user.
        """
        all_records = self.notification_store.read_all()
        remaining = [r for r in all_records if r.get("user_id") != user_id]
        self.notification_store.write_all(remaining)

    def get_user_notifications_raw(self, user_id: str) -> list[dict]:
        """Get raw notification dicts for a user (used by reminder_checker).

        Args:
            user_id: UUID4 string of the user.

        Returns:
            List of raw notification dicts for this user.
        """
        all_records = self.notification_store.read_all()
        return [r for r in all_records if r.get("user_id") == user_id]
