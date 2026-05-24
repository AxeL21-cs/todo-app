"""Attachment service handling image upload and retrieval for todos."""

import os
import uuid
from datetime import datetime, timezone

from exceptions import NotFoundError, ValidationError
from models import Attachment
from store import JSONStore

# Allowed image MIME types
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class AttachmentService:
    """Handles image attachment operations scoped to a todo."""

    def __init__(self, attachment_store: JSONStore, upload_dir: str):
        """Initialize with attachment store and upload directory.

        Args:
            attachment_store: JSONStore instance for attachment metadata persistence.
            upload_dir: Directory path where uploaded files are stored.
        """
        self.attachment_store = attachment_store
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    def create(
        self,
        user_id: str,
        todo_id: str,
        filename: str,
        content_type: str,
        file_data: bytes,
    ) -> Attachment:
        """Save an uploaded image attachment.

        Args:
            user_id: The authenticated user's ID.
            todo_id: The todo's ID to attach to.
            filename: Original filename from the upload.
            content_type: MIME type of the file.
            file_data: Raw file bytes.

        Returns:
            The created Attachment object.

        Raises:
            ValidationError: If file type is not allowed or file is too large.
        """
        # Validate content type
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ValidationError(
                [{"field": "file", "message": f"File type not allowed. Must be one of: {', '.join(ALLOWED_CONTENT_TYPES)}"}]
            )

        # Validate file size
        if len(file_data) > MAX_FILE_SIZE:
            raise ValidationError(
                [{"field": "file", "message": f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)} MB"}]
            )

        # Generate stored filename with UUID to avoid collisions
        ext = os.path.splitext(filename)[1].lower() or ".bin"
        stored_filename = f"{uuid.uuid4()}{ext}"

        # Write file to disk
        file_path = os.path.join(self.upload_dir, stored_filename)
        with open(file_path, "wb") as f:
            f.write(file_data)

        # Create metadata record
        attachment_data = {
            "id": str(uuid.uuid4()),
            "todo_id": todo_id,
            "user_id": user_id,
            "filename": filename,
            "stored_filename": stored_filename,
            "content_type": content_type,
            "size": len(file_data),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self.attachment_store.add(attachment_data)

        return Attachment(**attachment_data)

    def list_for_todo(self, todo_id: str) -> list[Attachment]:
        """List all attachments for a todo, ordered by created_at ASC.

        Args:
            todo_id: The todo's ID.

        Returns:
            List of Attachment objects, oldest first.
        """
        all_records = self.attachment_store.read_all()
        todo_attachments = [r for r in all_records if r.get("todo_id") == todo_id]

        # Sort by created_at ascending
        todo_attachments.sort(key=lambda r: r.get("created_at", ""))

        return [Attachment(**r) for r in todo_attachments]

    def get_by_id(self, attachment_id: str) -> Attachment | None:
        """Get an attachment by ID.

        Args:
            attachment_id: The attachment's ID.

        Returns:
            Attachment object or None if not found.
        """
        record = self.attachment_store.find_by_id(attachment_id)
        if not record:
            return None
        return Attachment(**record)

    def get_file_path(self, attachment: Attachment) -> str:
        """Get the full file path for an attachment.

        Args:
            attachment: The Attachment object.

        Returns:
            Full path to the stored file.
        """
        return os.path.join(self.upload_dir, attachment.stored_filename)

    def delete(self, user_id: str, attachment_id: str) -> None:
        """Delete an attachment (only the author can delete).

        Args:
            user_id: The authenticated user's ID.
            attachment_id: The attachment's ID to delete.

        Raises:
            NotFoundError: If attachment not found or not owned by user.
        """
        record = self.attachment_store.find_by_id(attachment_id)

        if not record or record.get("user_id") != user_id:
            raise NotFoundError("Attachment not found")

        # Delete file from disk
        file_path = os.path.join(self.upload_dir, record["stored_filename"])
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete metadata record
        deleted = self.attachment_store.delete(attachment_id)
        if not deleted:
            raise NotFoundError("Attachment not found")

    def delete_all_for_todo(self, todo_id: str) -> None:
        """Delete all attachments for a todo (used when todo is deleted).

        Args:
            todo_id: The todo's ID.
        """
        all_records = self.attachment_store.read_all()
        todo_attachments = [r for r in all_records if r.get("todo_id") == todo_id]

        # Delete files from disk
        for record in todo_attachments:
            file_path = os.path.join(self.upload_dir, record["stored_filename"])
            if os.path.exists(file_path):
                os.remove(file_path)

        # Remove metadata records
        remaining = [r for r in all_records if r.get("todo_id") != todo_id]
        self.attachment_store.write_all(remaining)
