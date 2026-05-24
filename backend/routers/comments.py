"""Comments router handling CRUD operations for todo comments."""

import os

from fastapi import APIRouter, Depends, Response

from dependencies import get_current_user
from exceptions import NotFoundError
from models import Comment, CommentCreate, CommentResponse, User
from services.comment_service import CommentService
from services.todo_service import TodoService
from store import JSONStore

# Initialize stores and services
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
comment_store = JSONStore(os.path.join(DATA_DIR, "comments.json"))
todo_store = JSONStore(os.path.join(DATA_DIR, "todos.json"))
comment_service = CommentService(comment_store)
todo_service = TodoService(todo_store)

# User store for resolving usernames
user_store = JSONStore(os.path.join(DATA_DIR, "users.json"))

router = APIRouter(prefix="/api/todos/{todo_id}/comments", tags=["comments"])


def _get_username(user_id: str) -> str:
    """Resolve a user_id to a username."""
    user_record = user_store.find_by_id(user_id)
    if user_record:
        return user_record.get("username", "Unknown")
    return "Unknown"


@router.get("", response_model=list[CommentResponse])
async def list_comments(
    todo_id: str,
    current_user: User = Depends(get_current_user),
) -> list[CommentResponse]:
    """List all comments for a todo.

    Verifies the user owns the todo, then returns comments ordered by created_at ASC.

    Args:
        todo_id: The todo's ID.
        current_user: The authenticated user (injected by dependency).

    Returns:
        List of CommentResponse objects.
    """
    # Verify todo exists and belongs to user
    todo_service.get_by_id(user_id=current_user.id, todo_id=todo_id)

    comments = comment_service.list_for_todo(todo_id)

    return [
        CommentResponse(
            id=c.id,
            todo_id=c.todo_id,
            user_id=c.user_id,
            username=_get_username(c.user_id),
            content=c.content,
            created_at=c.created_at,
        )
        for c in comments
    ]


@router.post("", response_model=CommentResponse, status_code=201)
async def create_comment(
    todo_id: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
) -> CommentResponse:
    """Create a comment on a todo.

    Verifies the user owns the todo, then creates the comment.

    Args:
        todo_id: The todo's ID.
        comment_data: The comment creation request body.
        current_user: The authenticated user (injected by dependency).

    Returns:
        The created CommentResponse with 201 status code.
    """
    # Verify todo exists and belongs to user
    todo_service.get_by_id(user_id=current_user.id, todo_id=todo_id)

    comment = comment_service.create(
        user_id=current_user.id,
        todo_id=todo_id,
        data=comment_data,
    )

    return CommentResponse(
        id=comment.id,
        todo_id=comment.todo_id,
        user_id=comment.user_id,
        username=current_user.username,
        content=comment.content,
        created_at=comment.created_at,
    )


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    todo_id: str,
    comment_id: str,
    current_user: User = Depends(get_current_user),
) -> Response:
    """Delete a comment (only the author can delete).

    Args:
        todo_id: The todo's ID.
        comment_id: The comment's ID to delete.
        current_user: The authenticated user (injected by dependency).

    Returns:
        204 No Content response on success.
    """
    # Verify todo exists and belongs to user
    todo_service.get_by_id(user_id=current_user.id, todo_id=todo_id)

    comment_service.delete(user_id=current_user.id, comment_id=comment_id)
    return Response(status_code=204)
