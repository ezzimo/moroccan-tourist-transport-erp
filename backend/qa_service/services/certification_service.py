"""
Service layer – QA service
"""
from __future__ import annotations

import logging
import uuid
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, UploadFile, status
from sqlmodel import Session, and_, func, select

from models.certification import (
    Certification,
    CertificationStatus,
    EntityType,
)
from schemas.certification import (
    CertificationCreate,
    CertificationResponse,
    CertificationUpdate,
)
from utils.notifications import send_certification_alert
from utils.upload import process_certificate_upload
from utils.validation import validate_certification_data

logger = logging.getLogger(__name__)


class CertificationService:
    """Business logic for certifications."""

    def __init__(self, session: Session):
        self.session = session

    # ───────────────────────── create ─────────────────────────
    async def create_certification(
        self,
        payload: CertificationCreate,
        created_by: uuid.UUID | None = None,
    ) -> CertificationResponse:
        errors = validate_certification_data(payload.model_dump())
        if errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "Validation failed", "errors": errors},
            )

        cert_number = await self._generate_cert_number()

        model = Certification(
            **payload.model_dump(exclude_none=True),
            certificate_number=cert_number,
            created_by=created_by,
            status=(
                CertificationStatus.ACTIVE
                if payload.issue_date <= date.today()
                else CertificationStatus.PENDING
            ),
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        logger.info("Created certification %s", model.certificate_number)
        return self._to_response(model)

    # ───────────────────────── read helpers ─────────────────────────
    async def get_certification(self, cert_id: uuid.UUID) -> CertificationResponse:
        model = self.session.get(Certification, cert_id)
        if not model:
            raise HTTPException(status_code=404, detail="Certification not found.")
        return self._to_response(model)

    async def get_certifications(
        self,
        skip: int = 0,
        limit: int = 100,
        entity_type: EntityType | None = None,
        entity_id: str | None = None,
        status: CertificationStatus | None = None,
        expiring_soon: bool = False,
        expired_only: bool = False,
    ) -> List[CertificationResponse]:
        q = select(Certification)
        cond: list[Any] = []
        if entity_type:
            cond.append(Certification.entity_type == entity_type)
        if entity_id:
            cond.append(Certification.entity_id == entity_id)
        if status:
            cond.append(Certification.status == status)
        if expiring_soon:
            edge = date.today() + timedelta(days=60)
            cond.extend(
                [
                    Certification.expiry_date.is_not(None),
                    Certification.expiry_date <= edge,
                    Certification.expiry_date > date.today(),
                    Certification.status == CertificationStatus.ACTIVE,
                ]
            )
        if expired_only:
            cond.extend(
                [
                    Certification.expiry_date.is_not(None),
                    Certification.expiry_date < date.today(),
                ]
            )
        if cond:
            q = q.where(and_(*cond))

        models = (
            self.session.exec(q.order_by(Certification.expiry_date.asc()).offset(skip).limit(limit)).all()
        )
        return [self._to_response(m) for m in models]

    # ───────────────────────── update ─────────────────────────
    async def update_certification(
        self, cert_id: uuid.UUID, patch: CertificationUpdate
    ) -> CertificationResponse:
        model = self.session.get(Certification, cert_id)
        if not model:
            raise HTTPException(status_code=404, detail="Certification not found.")

        for k, v in patch.model_dump(exclude_unset=True).items():
            setattr(model, k, v)

        # auto-status
        if model.expiry_date and model.expiry_date < date.today():
            model.status = CertificationStatus.EXPIRED
        elif model.issue_date <= date.today():
            model.status = CertificationStatus.ACTIVE

        model.updated_at = datetime.utcnow()
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_response(model)

    # ───────────────────────── renew / suspend / reactivate ─────────────────────────
    async def renew_certification(
        self,
        cert_id: uuid.UUID,
        new_issue_date: date,
        new_expiry_date: date,
        renewal_notes: str | None = None,
    ) -> CertificationResponse:
        if new_expiry_date <= new_issue_date:
            raise HTTPException(400, "Expiry date must be after issue date.")

        model = self.session.get(Certification, cert_id)
        if not model:
            raise HTTPException(404, "Certification not found.")

        model.issue_date = new_issue_date
        model.expiry_date = new_expiry_date
        model.status = CertificationStatus.ACTIVE
        model.renewal_notes = renewal_notes
        model.updated_at = datetime.utcnow()
        self.session.commit()
        self.session.refresh(model)
        return self._to_response(model)

    async def suspend_certification(
        self, cert_id: uuid.UUID, reason: str
    ) -> Dict[str, str]:
        model = self.session.get(Certification, cert_id)
        if not model:
            raise HTTPException(404, "Certification not found.")

        model.status = CertificationStatus.SUSPENDED
        model.suspension_reason = reason
        model.updated_at = datetime.utcnow()
        self.session.commit()

        # fire-and-forget alert
        try:
            await send_certification_alert(
                certification_id=str(cert_id),
                certification_data={
                    "certificate_number": model.certificate_number,
                    "name": model.name,
                    "entity_type": model.entity_type.value if model.entity_type else None,
                    "suspension_reason": reason,
                },
                notification_type="certification_suspended",
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Alert send failed: %s", exc)

        return {"message": "Certification suspended."}

    async def reactivate_certification(self, cert_id: uuid.UUID) -> Dict[str, str]:
        model = self.session.get(Certification, cert_id)
        if not model:
            raise HTTPException(404, "Certification not found.")
        if model.status != CertificationStatus.SUSPENDED:
            raise HTTPException(400, "Only suspended certifications can be reactivated.")
        if model.expiry_date and model.expiry_date < date.today():
            raise HTTPException(400, "Cannot reactivate expired certification.")

        model.status = CertificationStatus.ACTIVE
        model.suspension_reason = None
        model.updated_at = datetime.utcnow()
        self.session.commit()
        return {"message": "Certification reactivated."}

    # ───────────────────────── delete ─────────────────────────
    async def delete_certification(self, cert_id: uuid.UUID) -> Dict[str, str]:
        model = self.session.get(Certification, cert_id)
        if not model:
            raise HTTPException(404, "Certification not found.")

        if model.document_path:
            from utils.upload import delete_certificate_file

            try:
                delete_certificate_file(model.document_path)
            except Exception as exc:  # noqa: BLE001
                logger.warning("File delete failed: %s", exc)

        self.session.delete(model)
        self.session.commit()
        return {"message": "Certification deleted."}

    # ───────────────────────── helpers ─────────────────────────
    async def _generate_cert_number(self) -> str:
        prefix = f"CERT-{date.today():%Y%m}"
        last = (
            self.session.exec(
                select(Certification)
                .where(Certification.certificate_number.like(f"{prefix}%"))
                .order_by(Certification.certificate_number.desc())
            )
            .first()
        )
        n = 1 if not last else int(last.certificate_number.split("-")[-1]) + 1
        return f"{prefix}-{n:04d}"

    @staticmethod
    def _to_response(model: Certification) -> CertificationResponse:
        return CertificationResponse(
            **model.model_dump(),
            is_expired=model.is_expired(),
            days_until_expiry=model.days_until_expiry(),
            needs_renewal=model.needs_renewal(),
            is_valid=model.is_valid(),
            validity_period_days=model.get_validity_period_days(),
            renewal_start_date=model.calculate_renewal_start_date(),
        )

    # ───────────────────────── create + upload in one pass ─────────────────────────
    async def create_certification_with_file(
        self,
        payload: CertificationCreate,
        file: UploadFile | None,
        created_by: uuid.UUID | None = None,
    ) -> CertificationResponse:
        """
        Create a certification and, if a file is provided, store it and
        attach `document_path` / `mime_type` meta-data.
        """
        cert = await self.create_certification(payload, created_by)

        if file:
            # store file, then update the cert with the resulting path
            upload_info = await process_certificate_upload(file, cert.id)
            model = self.session.get(Certification, cert.id)
            model.document_path = upload_info["file_path"]
            model.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(model)
            cert.document_path = model.document_path  # reflect in response

        return cert

    # ───────────────────────── stand-alone upload endpoint ─────────────────────────
    async def upload_certificate_document(
        self,
        cert_id: uuid.UUID,
        file: UploadFile,
        uploaded_by: uuid.UUID | None = None,       # kept for audit logs later
    ) -> CertificationResponse:
        """
        Attach / replace a document for an existing certification.
        """
        model = self.session.get(Certification, cert_id)
        if not model:
            raise HTTPException(404, "Certification not found.")

        upload_info = await process_certificate_upload(file, cert_id)
        model.document_path = upload_info["file_path"]
        model.updated_at = datetime.utcnow()
        self.session.commit()
        self.session.refresh(model)
        return self._to_response(model)