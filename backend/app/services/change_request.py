"""Service layer for change request moderation workflow."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Mapping, MutableMapping, Sequence

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlmodel import Session, select

from app.models import ChangeRequest, ChangeRequestStatus, ReviewTargetType, User, UserRole
from app.schemas.change_request import ChangeRequestCreate, ChangeRequestRead
from app.schemas.course import CourseUpdate
from app.schemas.institution import InstitutionUpdate
from app.schemas.professor import ProfessorUpdate
from app.schemas.subject import SubjectUpdate
from app.services.course import get_course, update_course
from app.services.institution import InstitutionService
from app.services.professor import ProfessorService
from app.services.subject import SubjectService


class ChangeRequestService:
    """Encapsulates business rules for creating and moderating change requests."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_change_requests(
        self,
        *,
        status_filter: ChangeRequestStatus | None = None,
        target_type: ReviewTargetType | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ChangeRequestRead]:
        """Return change requests optionally filtered by status and target."""

        statement = (
            select(ChangeRequest)
            .order_by(ChangeRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        if status_filter is not None:
            statement = statement.where(ChangeRequest.status == status_filter)

        if target_type is not None:
            statement = statement.where(ChangeRequest.target_type == target_type)

        results = self.session.exec(statement).all()
        return [ChangeRequestRead.model_validate(item) for item in results]

    def get_change_request(self, change_request_id: int) -> ChangeRequest:
        """Retrieve a single change request by its identifier."""

        change_request = self.session.get(ChangeRequest, change_request_id)
        if change_request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Change request not found.",
            )
        return change_request

    def create_change_request(
        self,
        payload: ChangeRequestCreate,
        *,
        current_user: User,
    ) -> ChangeRequestRead:
        """Create a new change request submitted by any authenticated user."""

        if current_user.id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authenticated user context is required.",
            )

        normalized_payload = self._normalize_payload(payload.payload)

        change_request = ChangeRequest(
            target_type=payload.target_type,
            payload=normalized_payload,
            status=ChangeRequestStatus.PENDING,
            created_by=current_user.id,
        )
        self.session.add(change_request)
        self.session.commit()
        self.session.refresh(change_request)
        return ChangeRequestRead.model_validate(change_request)

    def moderate_change_request(
        self,
        change_request_id: int,
        *,
        new_status: ChangeRequestStatus,
        current_user: User,
    ) -> ChangeRequestRead:
        """Approve or reject a change request, applying updates when approved."""

        if current_user.role != UserRole.MODERATOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only moderators may resolve change requests.",
            )

        if new_status not in {
            ChangeRequestStatus.APPROVED,
            ChangeRequestStatus.REJECTED,
        }:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid status transition for moderation.",
            )

        change_request = self.get_change_request(change_request_id)

        if change_request.status != ChangeRequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only pending change requests may be resolved.",
            )

        with self.session.begin():
            if new_status == ChangeRequestStatus.APPROVED:
                self._apply_updates(change_request)

            change_request.status = new_status
            change_request.resolved_by = current_user.id
            change_request.resolved_at = datetime.utcnow()

            self.session.add(change_request)

        self.session.refresh(change_request)
        return ChangeRequestRead.model_validate(change_request)

    def _normalize_payload(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        """Ensure the payload includes a normalized target identifier and data block."""

        if not isinstance(payload, Mapping):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="payload must be an object.",
            )

        target_id = self._extract_target_id(payload)
        updates = self._extract_updates(payload)

        normalized: Dict[str, Any] = dict(payload)
        normalized["target_id"] = target_id
        normalized.pop("id", None)

        if "changes" in normalized and isinstance(normalized["changes"], Mapping):
            normalized["changes"] = updates
        elif "data" in normalized and isinstance(normalized["data"], Mapping):
            normalized["data"] = updates
        else:
            normalized["changes"] = updates

        return normalized

    def _extract_target_id(self, payload: Mapping[str, Any]) -> int:
        """Retrieve and validate the target identifier from a payload mapping."""

        candidate = payload.get("target_id", payload.get("id"))
        if candidate is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Change request payload must include target_id.",
            )

        try:
            target_id = int(candidate)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="target_id must be an integer.",
            ) from None

        if target_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="target_id must be a positive integer.",
            )
        return target_id

    def _extract_updates(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        """Return the update mapping contained within the payload."""

        update_mapping: Mapping[str, Any] | None = None
        for key in ("changes", "data"):
            candidate = payload.get(key)
            if isinstance(candidate, Mapping):
                update_mapping = candidate
                break

        if update_mapping is None:
            filtered: MutableMapping[str, Any] = {
                key: value
                for key, value in payload.items()
                if key not in {"target_id", "id", "metadata"}
            }
            update_mapping = filtered

        if not update_mapping:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Change request payload must include at least one field to update.",
            )

        if not isinstance(update_mapping, Mapping):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Change request payload changes must be an object.",
            )

        return dict(update_mapping)

    def _apply_updates(self, change_request: ChangeRequest) -> None:
        """Apply approved updates to the corresponding target entity."""

        target_id = self._extract_target_id(change_request.payload)
        update_data = self._extract_updates(change_request.payload)

        match change_request.target_type:
            case ReviewTargetType.INSTITUTION:
                self._update_institution(target_id, update_data)
            case ReviewTargetType.COURSE:
                self._update_course(target_id, update_data)
            case ReviewTargetType.PROFESSOR:
                self._update_professor(target_id, update_data)
            case ReviewTargetType.SUBJECT:
                self._update_subject(target_id, update_data)
            case _:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Unsupported change request target type.",
                )

    def _update_institution(self, institution_id: int, update_data: Mapping[str, Any]) -> None:
        """Apply approved updates to an institution through its service."""

        try:
            payload = InstitutionUpdate(**update_data)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid institution update payload.",
            ) from exc

        service = InstitutionService(self.session)
        service.update_institution(institution_id, payload, commit=False)

    def _update_course(self, course_id: int, update_data: Mapping[str, Any]) -> None:
        """Apply approved updates to a course using existing course services."""

        try:
            payload = CourseUpdate(**update_data)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid course update payload.",
            ) from exc

        course = get_course(self.session, course_id)
        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )
        update_payload = payload.model_dump(exclude_unset=True)
        update_course(
            self.session,
            course,
            update_payload,
            commit=False,
            refresh=False,
        )

    def _update_professor(self, professor_id: int, update_data: Mapping[str, Any]) -> None:
        """Apply approved updates to a professor through its service."""

        try:
            payload = ProfessorUpdate(**update_data)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid professor update payload.",
            ) from exc

        service = ProfessorService(self.session)
        service.update_professor(professor_id, payload, commit=False)

    def _update_subject(self, subject_id: int, update_data: Mapping[str, Any]) -> None:
        """Apply approved updates to a subject through its service."""

        try:
            payload = SubjectUpdate(**update_data)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid subject update payload.",
            ) from exc

        service = SubjectService(self.session)
        service.update_subject(subject_id, payload, commit=False)


__all__ = ["ChangeRequestService"]

