"""Comment service handling CRUD operations for todo comments."""

import uuid
from datetime import datetime, timezone

from exceptions import NotFoundError, ValidationError
from models import Comment, CommentCreate
from store import JSONStore


class CommentService:
    """Handles CRUD operations on comments scoped to a todo."""

    def __init__(self, comment_store: JSONStore):
        """Initialize with comment store.

        Args:
            comment_store: JSONStore instance for comment persistence.
        """
        self.comment_store = comment_store

    def create(self, user_id: str, todo_id: str, data: CommentCreate) -> Comment:
        """Create a comment on a todo.

        Args:
            user_id: The authenticated user's ID.
            todo_id: The todo's ID to comment on.
            data: CommentCreate model with content.

        Returns:
            The created Comment object.

        Raises:
            ValidationError: If content is blank.
        """
        if not data.content or not data.content.strip():
            raise ValidationError([{"field": "content", "message": "Comment must not be blank"}])

        comment_data = {
            "id": str(uuid.uuid4()),
            "todo_id": todo_id,
            "user_id": user_id,
            "content": data.content.strip(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self.comment_store.add(comment_data)

        return Comment(**comment_data)

    def list_for_todo(self, todo_id: str) -> list[Comment]:
        """List all comments for a todo, ordered by created_at ASC.

        Args:
            todo_id: The todo's ID.

        Returns:
            List of Comment objects, oldest first.
        """
        all_records = self.comment_store.read_all()
        todo_comments = [r for r in all_records if r.get("todo_id") == todo_id]

        # Sort by created_at ascending (oldest first)
        todo_comments.sort(key=lambda r: r.get("created_at", ""))

        return [Comment(**r) for r in todo_comments]

    def delete(self, user_id: str, comment_id: str) -> None:
        """Delete a comment (only the author can delete).

        Args:
            user_id: The authenticated user's ID.
            comment_id: The comment's ID to delete.

        Raises:
            NotFoundError: If comment not found or not owned by user.
        """
        record = self.comment_store.find_by_id(comment_id)

        if not record or record.get("user_id") != user_id:
            raise NotFoundError("Comment not found")

        deleted = self.comment_store.delete(comment_id)
        if not deleted:
            raise NotFoundError("Comment not found")

    def delete_all_for_todo(self, todo_id: str) -> None:
        """Delete all comments for a todo (used when todo is deleted).

        Args:
            todo_id: The todo's ID.
        """
        all_records = self.comment_store.read_all()
        remaining = [r for r in all_records if r.get("todo_id") != todo_id]
        self.comment_store.write_all(remaining)
