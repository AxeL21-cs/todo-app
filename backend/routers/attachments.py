"""Attachments router handling image upload and retrieval for todos."""

import os

from fastapi import APIRouter, Depends, Response, UploadFile, File
from fastapi.responses import FileResponse

from dependencies import get_current_user
from exceptions import NotFoundError
from models import AttachmentResponse, User
from services.attachment_service import AttachmentService
from services.todo_service import TodoService
from store import JSONStore

# Initialize stores and services
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
attachment_store = JSONStore(os.path.join(DATA_DIR, "attachments.json"))
todo_store = JSONStore(os.path.join(DATA_DIR, "todos.json"))
attachment_service = AttachmentService(attachment_store, UPLOAD_DIR)
todo_service = TodoService(todo_store)

router = APIRouter(prefix="/api/todos/{todo_id}/attachments", tags=["attachments"])


@router.get("", response_model=list[AttachmentResponse])
async def list_attachments(
    todo_id: str,
    current_user: User = Depends(get_current_user),
) -> list[AttachmentResponse]:
    """List all attachments for a todo.

    Verifies the user owns the todo, then returns attachments ordered by created_at ASC.

    Args:
        todo_id: The todo's ID.
        current_user: The authenticated user (injected by dependency).

    Returns:
        List of AttachmentResponse objects.
    """
    # Verify todo exists and belongs to user
    todo_service.get_by_id(user_id=current_user.id, todo_id=todo_id)

    attachments = attachment_service.list_for_todo(todo_id)

    return [
        AttachmentResponse(
            id=a.id,
            todo_id=a.todo_id,
            user_id=a.user_id,
            filename=a.filename,
            content_type=a.content_type,
            size=a.size,
            url=f"/api/todos/{todo_id}/attachments/{a.id}/file",
            created_at=a.created_at,
        )
        for a in attachments
    ]


@router.post("", response_model=AttachmentResponse, status_code=201)
async def upload_attachment(
    todo_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> AttachmentResponse:
    """Upload an image attachment to a todo.

    Accepts image files (JPEG, PNG, GIF, WebP) up to 5 MB.

    Args:
        todo_id: The todo's ID.
        file: The uploaded file.
        current_user: The authenticated user (injected by dependency).

    Returns:
        The created AttachmentResponse with 201 status code.
    """
    # Verify todo exists and belongs to user
    todo_service.get_by_id(user_id=current_user.id, todo_id=todo_id)

    # Read file data
    file_data = await file.read()

    attachment = attachment_service.create(
        user_id=current_user.id,
        todo_id=todo_id,
        filename=file.filename or "unnamed",
        content_type=file.content_type or "application/octet-stream",
        file_data=file_data,
    )

    return AttachmentResponse(
        id=attachment.id,
        todo_id=attachment.todo_id,
        user_id=attachment.user_id,
        filename=attachment.filename,
        content_type=attachment.content_type,
        size=attachment.size,
        url=f"/api/todos/{todo_id}/attachments/{attachment.id}/file",
        created_at=attachment.created_at,
    )


@router.get("/{attachment_id}/file")
async def download_attachment(
    todo_id: str,
    attachment_id: str,
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    """Download an attachment file.

    Args:
        todo_id: The todo's ID.
        attachment_id: The attachment's ID.
        current_user: The authenticated user (injected by dependency).

    Returns:
        The file as a response.
    """
    # Verify todo exists and belongs to user
    todo_service.get_by_id(user_id=current_user.id, todo_id=todo_id)

    attachment = attachment_service.get_by_id(attachment_id)
    if not attachment or attachment.todo_id != todo_id:
        raise NotFoundError("Attachment not found")

    file_path = attachment_service.get_file_path(attachment)
    if not os.path.exists(file_path):
        raise NotFoundError("Attachment file not found")

    return FileResponse(
        path=file_path,
        media_type=attachment.content_type,
        filename=attachment.filename,
    )


@router.delete("/{attachment_id}", status_code=204)
async def delete_attachment(
    todo_id: str,
    attachment_id: str,
    current_user: User = Depends(get_current_user),
) -> Response:
    """Delete an attachment (only the author can delete).

    Args:
        todo_id: The todo's ID.
        attachment_id: The attachment's ID to delete.
        current_user: The authenticated user (injected by dependency).

    Returns:
        204 No Content response on success.
    """
    # Verify todo exists and belongs to user
    todo_service.get_by_id(user_id=current_user.id, todo_id=todo_id)

    attachment_service.delete(user_id=current_user.id, attachment_id=attachment_id)
    return Response(status_code=204)
