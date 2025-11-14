"""Service layer implementing review business rules."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Callable, Mapping, MutableMapping

from fastapi import HTTPException, status
from sqlalchemy.sql import func
from sqlmodel import Session, select

from app.models import (
    Course,
    Institution,
    Professor,
    Review,
    ReviewTargetType,
    Subject,
    User,
    UserRole,
)
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate

_TargetModelGetter = Callable[[Session, int], Any]


class ReviewService:
    """Encapsulate all review-related business logic."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_reviews(
        self,
        *,
        target_type: ReviewTargetType | None = None,
        target_id: int | None = None,
        user_id: int | None = None,
        include_pending: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ReviewRead]:
        """Return reviews filtered by target and visibility rules."""

        statement = select(Review).order_by(Review.created_at.desc()).offset(skip).limit(limit)

        if not include_pending:
            statement = statement.where(Review.approved.is_(True))

        if target_type is not None:
            statement = statement.where(Review.target_type == target_type)
            if target_id is not None:
                target_field = self._target_field_for_type(target_type)
                statement = statement.where(getattr(Review, target_field) == target_id)
        elif target_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="target_type is required when filtering by target_id.",
            )

        if user_id is not None:
            statement = statement.where(Review.user_id == user_id)

        reviews = self.session.exec(statement).all()
        return [ReviewRead.model_validate(review) for review in reviews]

    def get_review(self, review_id: int, *, include_pending: bool = False) -> Review:
        """Retrieve a review enforcing visibility of pending entries."""

        review = self.session.get(Review, review_id)
        if review is None or (not include_pending and not review.approved):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found.",
            )
        return review

    def create_review(self, payload: ReviewCreate, *, current_user: User) -> ReviewRead:
        """Create a review ensuring role restrictions and uniqueness."""

        if current_user.role != UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can create reviews.",
            )

        target_type = payload.target_type
        target_field = self._target_field_for_type(target_type)
        target_id = self._extract_target_id(payload, target_field)

        self._ensure_target_exists(target_type, target_id)
        self._ensure_unique_review(
            user_id=current_user.id,
            target_type=target_type,
            target_field=target_field,
            target_id=target_id,
        )

        text = payload.text.strip()
        if not text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Review text cannot be empty.",
            )

        review_data: MutableMapping[str, Any] = {
            "user_id": current_user.id,
            "target_type": target_type,
            "rating_1": self._validate_rating(payload.rating_1, "rating_1"),
            "rating_2": self._validate_rating(payload.rating_2, "rating_2"),
            "rating_3": self._validate_rating(payload.rating_3, "rating_3"),
            "rating_4": self._validate_rating(payload.rating_4, "rating_4"),
            "rating_5": self._validate_rating(payload.rating_5, "rating_5"),
            "text": text,
            "approved": False,
        }

        # Assign the selected target identifier and reset the others explicitly.
        for field in ("institution_id", "course_id", "professor_id", "subject_id"):
            review_data[field] = target_id if field == target_field else None

        review = Review(**review_data)
        self.session.add(review)
        self.session.commit()
        self.session.refresh(review)
        return ReviewRead.model_validate(review)

    def update_review(
        self,
        review_id: int,
        payload: ReviewUpdate,
        *,
        current_user: User,
    ) -> ReviewRead:
        """Update review content while respecting moderation rules."""

        review = self.get_review(review_id, include_pending=True)
        is_moderator = current_user.role == UserRole.MODERATOR
        is_author = review.user_id == current_user.id

        update_data = payload.model_dump(exclude_unset=True)

        editable_fields = {"rating_1", "rating_2", "rating_3", "rating_4", "rating_5", "text"}
        requested_edit = editable_fields.intersection(update_data)
        if requested_edit:
            if not (is_author or is_moderator):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to edit this review.",
                )
            if review.approved:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Approved reviews cannot be edited.",
                )

        if "approved" in update_data:
            if not is_moderator:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only moderators may change approval status.",
                )
            review.approved = bool(update_data["approved"])

        for field in requested_edit:
            value = update_data[field]
            if value is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"{field} cannot be null.",
                )

            if field == "text":
                text_value = value.strip()
                if not text_value:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Review text cannot be empty.",
                    )
                setattr(review, field, text_value)
                continue

            rating_value = self._validate_rating(int(value), field)
            setattr(review, field, rating_value)

        self.session.add(review)
        self.session.commit()
        self.session.refresh(review)
        return ReviewRead.model_validate(review)

    def delete_review(self, review_id: int, *, current_user: User) -> None:
        """Delete a review; moderators can always delete, authors until approval."""

        review = self.get_review(review_id, include_pending=True)
        is_moderator = current_user.role == UserRole.MODERATOR
        is_author = review.user_id == current_user.id

        if not (is_moderator or (is_author and not review.approved)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this review.",
            )

        self.session.delete(review)
        self.session.commit()

    def ensure_can_comment(self, review_id: int) -> Review:
        """Ensure comments can be created only for approved reviews."""

        review = self.get_review(review_id, include_pending=True)
        if not review.approved:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Comments are allowed only on approved reviews.",
            )
        return review

    def compute_metrics(
        self,
        *,
        target_type: ReviewTargetType,
        target_id: int,
    ) -> Mapping[str, float | int | None]:
        """Return aggregated metrics excluding pending reviews."""

        target_field = self._target_field_for_type(target_type)

        statement = (
            select(
                func.count(Review.id),
                func.avg(Review.rating_1),
                func.avg(Review.rating_2),
                func.avg(Review.rating_3),
                func.avg(Review.rating_4),
                func.avg(Review.rating_5),
            )
            .where(Review.target_type == target_type)
            .where(getattr(Review, target_field) == target_id)
            .where(Review.approved.is_(True))
        )

        count, avg1, avg2, avg3, avg4, avg5 = self.session.exec(statement).one()
        overall = None
        if count and all(avg is not None for avg in (avg1, avg2, avg3, avg4, avg5)):
            overall = float(avg1 + avg2 + avg3 + avg4 + avg5) / 5

        return {
            "count": int(count or 0),
            "average_rating_1": float(avg1) if avg1 is not None else None,
            "average_rating_2": float(avg2) if avg2 is not None else None,
            "average_rating_3": float(avg3) if avg3 is not None else None,
            "average_rating_4": float(avg4) if avg4 is not None else None,
            "average_rating_5": float(avg5) if avg5 is not None else None,
            "average_overall": overall,
        }

    def _target_field_for_type(self, target_type: ReviewTargetType) -> str:
        mapping: Mapping[ReviewTargetType, str] = {
            ReviewTargetType.INSTITUTION: "institution_id",
            ReviewTargetType.COURSE: "course_id",
            ReviewTargetType.PROFESSOR: "professor_id",
            ReviewTargetType.SUBJECT: "subject_id",
        }
        return mapping[target_type]

    def _extract_target_id(self, payload: ReviewCreate, target_field: str) -> int:
        value = getattr(payload, target_field)
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{target_field} is required for the selected target type.",
            )

        # Ensure no conflicting target identifiers were provided.
        conflicting_fields = {
            field
            for field in ("institution_id", "course_id", "professor_id", "subject_id")
            if field != target_field and getattr(payload, field) is not None
        }
        if conflicting_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only one target identifier must be provided.",
            )
        return int(value)

    def _ensure_target_exists(self, target_type: ReviewTargetType, target_id: int) -> None:
        model_getters: Mapping[ReviewTargetType, _TargetModelGetter] = {
            ReviewTargetType.INSTITUTION: lambda session, pk: session.get(Institution, pk),
            ReviewTargetType.COURSE: lambda session, pk: session.get(Course, pk),
            ReviewTargetType.PROFESSOR: lambda session, pk: session.get(Professor, pk),
            ReviewTargetType.SUBJECT: lambda session, pk: session.get(Subject, pk),
        }

        model_getter = model_getters[target_type]
        target = model_getter(self.session, target_id)
        if target is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target entity not found.",
            )

    def _ensure_unique_review(
        self,
        *,
        user_id: int,
        target_type: ReviewTargetType,
        target_field: str,
        target_id: int,
    ) -> None:
        statement = select(Review).where(
            Review.user_id == user_id,
            Review.target_type == target_type,
            getattr(Review, target_field) == target_id,
        )

        if self.session.exec(statement).first() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already submitted a review for this target.",
            )

    def _validate_rating(self, value: int, field: str) -> int:
        if not 1 <= int(value) <= 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} must be between 1 and 5.",
            )
        return int(value)


__all__ = ["ReviewService"]
