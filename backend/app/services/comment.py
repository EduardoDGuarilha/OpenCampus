"""Service layer for managing review comments."""

from __future__ import annotations

from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Comment, User, UserRole
from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from app.services.review import ReviewService


class CommentService:
    """Encapsulate comment business rules and persistence logic."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.review_service = ReviewService(session)

    def list_comments(self, review_id: int, *, skip: int = 0, limit: int = 100) -> Sequence[CommentRead]:
        """Return comments for an approved review respecting LGPD."""

        # Ensure the review exists and is visible for public consumption.
        self.review_service.get_review(review_id, include_pending=False)

        statement = (
            select(Comment)
            .where(Comment.review_id == review_id)
            .order_by(Comment.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        comments = self.session.exec(statement).all()
        return [CommentRead.model_validate(comment) for comment in comments]

    def get_comment(self, comment_id: int) -> Comment:
        """Retrieve a single comment entity."""

        comment = self.session.get(Comment, comment_id)
        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found.",
            )
        return comment

    def create_comment(self, payload: CommentCreate, *, current_user: User) -> CommentRead:
        """Create a comment on an approved review for any authenticated user."""

        review = self.review_service.ensure_can_comment(payload.review_id)

        text = payload.text.strip()
        if not text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Comment text cannot be empty.",
            )

        comment = Comment(
            user_id=current_user.id,
            review_id=review.id,
            text=text,
            is_official=self._is_official_author(current_user),
        )

        self.session.add(comment)
        self.session.commit()
        self.session.refresh(comment)
        return CommentRead.model_validate(comment)

    def update_comment(self, comment_id: int, payload: CommentUpdate, *, current_user: User) -> CommentRead:
        """Update comment content keeping official marker consistent."""

        comment = self.get_comment(comment_id)

        if comment.user_id != current_user.id and current_user.role != UserRole.MODERATOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit this comment.",
            )

        update_data = payload.model_dump(exclude_unset=True)
        if "text" in update_data:
            new_text = (update_data["text"] or "").strip()
            if not new_text:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Comment text cannot be empty.",
                )
            comment.text = new_text

        # Re-evaluate the official flag based on the author's current status.
        author = self.session.get(User, comment.user_id)
        if author is None:
            # The author should always exist; treat missing author as server inconsistency.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Comment author record is missing.",
            )
        comment.is_official = self._is_official_author(author)

        self.session.add(comment)
        self.session.commit()
        self.session.refresh(comment)
        return CommentRead.model_validate(comment)

    def delete_comment(self, comment_id: int, *, current_user: User) -> None:
        """Delete a comment when authorized."""

        comment = self.get_comment(comment_id)

        if comment.user_id != current_user.id and current_user.role != UserRole.MODERATOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this comment.",
            )

        self.session.delete(comment)
        self.session.commit()

    def _is_official_author(self, user: User) -> bool:
        """Return True when the user is a validated professor or institution."""

        return user.validated and user.role in {UserRole.PROFESSOR, UserRole.INSTITUTION}


__all__ = ["CommentService"]
