"""
Report service for QA reporting and analytics operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.quality_audit import QualityAudit, AuditStatus
from models.nonconformity import NonConformity, Severity, NCStatus
from models.compliance_requirement import ComplianceRequirement, ComplianceStatus
from models.certification import Certification, CertificationStatus
from services.audit_service import AuditService
from services.nonconformity_service import NonConformityService
from services.compliance_service import ComplianceService
from services.certification_service import CertificationService
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class ReportComplianceDomain(str, Enum):
    """Report domain enumeration"""
    AUDITS = "audits"
    NONCONFORMITIES = "nonconformities"
    COMPLIANCE = "compliance"
    CERTIFICATIONS = "certifications"
    OVERALL = "overall"


class ReportService:
    """Service for handling QA reporting and analytics operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.audit_service = AuditService(session)
        self.nonconformity_service = NonConformityService(session)
        self.compliance_service = ComplianceService(session)
        self.certification_service = CertificationService(session)
    
    async def generate_domain_report(
        self,
        domain: ReportComplianceDomain,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive report for specific domain
        
        Args:
            domain: Report domain (audits, nonconformities, etc.)
            start_date: Report start date
            end_date: Report end date
            entity_type: Filter by entity type
            entity_id: Filter by specific entity
            
        Returns:
            Comprehensive domain report
        """
        if domain == ReportComplianceDomain.AUDITS:
            return await self._generate_audit_report(start_date, end_date, entity_type, entity_id)
        elif domain == ReportComplianceDomain.NONCONFORMITIES:
            return await self._generate_nonconformity_report(start_date, end_date)
        elif domain == ReportComplianceDomain.COMPLIANCE:
            return await self._generate_compliance_report(start_date, end_date)
        elif domain == ReportComplianceDomain.CERTIFICATIONS:
            return await self._generate_certification_report(start_date, end_date)
        elif domain == ReportComplianceDomain.OVERALL:
            return await self._generate_overall_report(start_date, end_date)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown report domain: {domain}"
            )
    
    async def _generate_audit_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        # Get audit analytics
        audit_analytics = await self.audit_service.get_audit_analytics(
            start_date=start_date,
            end_date=end_date,
            entity_type=entity_type,
            entity_id=entity_id
        )
        
        # Get detailed audit data
        query = select(QualityAudit)
        conditions = []
        
        if start_date:
            conditions.append(QualityAudit.audit_date >= start_date)
        if end_date:
            conditions.append(QualityAudit.audit_date <= end_date)
        if entity_type:
            conditions.append(QualityAudit.entity_type == entity_type)
        if entity_id:
            conditions.append(QualityAudit.entity_id == entity_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        audits = self.session.exec(query).all()
        
        # Performance by auditor
        auditor_performance = {}
        for audit in audits:
            auditor_id = str(audit.auditor_id)
            if auditor_id not in auditor_performance:
                auditor_performance[auditor_id] = {
                    "total_audits": 0,
                    "completed_audits": 0,
                    "average_score": 0,
                    "total_score": 0
                }
            
            auditor_performance[auditor_id]["total_audits"] += 1
            if audit.status == AuditStatus.COMPLETED:
                auditor_performance[auditor_id]["completed_audits"] += 1
                if audit.score:
                    auditor_performance[auditor_id]["total_score"] += audit.score
        
        # Calculate averages
        for auditor_data in auditor_performance.values():
            if auditor_data["completed_audits"] > 0:
                auditor_data["average_score"] = auditor_data["total_score"] / auditor_data["completed_audits"]
        
        # Entity performance
        entity_performance = {}
        for audit in audits:
            entity_key = f"{audit.entity_type}:{audit.entity_id}"
            if entity_key not in entity_performance:
                entity_performance[entity_key] = {
                    "entity_type": audit.entity_type,
                    "entity_id": str(audit.entity_id),
                    "total_audits": 0,
                    "average_score": 0,
                    "total_score": 0,
                    "completed_audits": 0
                }
            
            entity_performance[entity_key]["total_audits"] += 1
            if audit.status == AuditStatus.COMPLETED and audit.score:
                entity_performance[entity_key]["completed_audits"] += 1
                entity_performance[entity_key]["total_score"] += audit.score
        
        # Calculate entity averages
        for entity_data in entity_performance.values():
            if entity_data["completed_audits"] > 0:
                entity_data["average_score"] = entity_data["total_score"] / entity_data["completed_audits"]
        
        return {
            "report_type": "audit_report",
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "summary": audit_analytics,
            "auditor_performance": auditor_performance,
            "entity_performance": list(entity_performance.values()),
            "recommendations": self._generate_audit_recommendations(audits),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_nonconformity_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive non-conformity report"""
        # Get non-conformity analytics
        nc_analytics = await self.nonconformity_service.get_nonconformity_analytics(
            start_date=start_date,
            end_date=end_date
        )
        
        # Get detailed non-conformity data
        query = select(NonConformity)
        conditions = []
        
        if start_date:
            conditions.append(NonConformity.created_at >= start_date)
        if end_date:
            conditions.append(NonConformity.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        nonconformities = self.session.exec(query).all()
        
        # Root cause analysis
        root_causes = {}
        for nc in nonconformities:
            if nc.root_cause:
                root_causes[nc.root_cause] = root_causes.get(nc.root_cause, 0) + 1
        
        # Monthly trends
        monthly_trends = {}
        for nc in nonconformities:
            month_key = nc.created_at.strftime("%Y-%m")
            if month_key not in monthly_trends:
                monthly_trends[month_key] = {
                    "month": month_key,
                    "total": 0,
                    "critical": 0,
                    "major": 0,
                    "moderate": 0,
                    "minor": 0,
                    "resolved": 0
                }
            
            monthly_trends[month_key]["total"] += 1
            monthly_trends[month_key][nc.severity.value.lower()] += 1
            if nc.status in [NCStatus.RESOLVED, NCStatus.CLOSED]:
                monthly_trends[month_key]["resolved"] += 1
        
        return {
            "report_type": "nonconformity_report",
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "summary": nc_analytics,
            "root_cause_analysis": root_causes,
            "monthly_trends": sorted(monthly_trends.values(), key=lambda x: x["month"]),
            "recommendations": self._generate_nc_recommendations(nonconformities),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_compliance_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        # Get compliance analytics
        compliance_analytics = await self.compliance_service.get_compliance_analytics()
        
        # Get detailed compliance data
        query = select(ComplianceRequirement)
        requirements = self.session.exec(query).all()
        
        # Compliance by domain
        domain_compliance = {}
        for req in requirements:
            domain = req.domain
            if domain not in domain_compliance:
                domain_compliance[domain] = {
                    "total": 0,
                    "met": 0,
                    "pending": 0,
                    "expired": 0,
                    "compliance_rate": 0
                }
            
            domain_compliance[domain]["total"] += 1
            domain_compliance[domain][req.status.value.lower()] += 1
        
        # Calculate compliance rates
        for domain_data in domain_compliance.values():
            if domain_data["total"] > 0:
                domain_data["compliance_rate"] = domain_data["met"] / domain_data["total"] * 100
        
        # Upcoming renewals
        upcoming_renewals = []
        alert_date = date.today() + timedelta(days=60)
        
        for req in requirements:
            if req.next_review_date and req.next_review_date <= alert_date:
                upcoming_renewals.append({
                    "requirement_id": str(req.id),
                    "description": req.description,
                    "domain": req.domain,
                    "next_review_date": req.next_review_date.isoformat(),
                    "days_until_review": (req.next_review_date - date.today()).days
                })
        
        return {
            "report_type": "compliance_report",
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "summary": compliance_analytics,
            "domain_compliance": domain_compliance,
            "upcoming_renewals": sorted(upcoming_renewals, key=lambda x: x["days_until_review"]),
            "recommendations": self._generate_compliance_recommendations(requirements),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_certification_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive certification report"""
        # Get certification analytics
        cert_analytics = await self.certification_service.get_certification_analytics()
        
        # Get detailed certification data
        query = select(Certification)
        certifications = self.session.exec(query).all()
        
        # Certifications by entity
        entity_certifications = {}
        for cert in certifications:
            entity_key = f"{cert.related_entity}:{cert.entity_id}" if cert.entity_id else cert.related_entity
            if entity_key not in entity_certifications:
                entity_certifications[entity_key] = {
                    "entity": cert.related_entity,
                    "entity_id": str(cert.entity_id) if cert.entity_id else None,
                    "total": 0,
                    "active": 0,
                    "expired": 0,
                    "suspended": 0
                }
            
            entity_certifications[entity_key]["total"] += 1
            entity_certifications[entity_key][cert.status.value.lower()] += 1
        
        # Expiring certifications
        expiring_certs = []
        alert_date = date.today() + timedelta(days=60)
        
        for cert in certifications:
            if cert.expiry_date and cert.expiry_date <= alert_date and cert.status == CertificationStatus.ACTIVE:
                expiring_certs.append({
                    "certification_id": str(cert.id),
                    "name": cert.name,
                    "issuing_body": cert.issuing_body,
                    "expiry_date": cert.expiry_date.isoformat(),
                    "days_until_expiry": (cert.expiry_date - date.today()).days,
                    "related_entity": cert.related_entity
                })
        
        return {
            "report_type": "certification_report",
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "summary": cert_analytics,
            "entity_certifications": list(entity_certifications.values()),
            "expiring_certifications": sorted(expiring_certs, key=lambda x: x["days_until_expiry"]),
            "recommendations": self._generate_certification_recommendations(certifications),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_overall_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive overall QA report"""
        # Get all analytics
        audit_analytics = await self.audit_service.get_audit_analytics(start_date=start_date, end_date=end_date)
        nc_analytics = await self.nonconformity_service.get_nonconformity_analytics(start_date=start_date, end_date=end_date)
        compliance_analytics = await self.compliance_service.get_compliance_analytics()
        cert_analytics = await self.certification_service.get_certification_analytics()
        
        # Calculate overall QA score
        audit_score = audit_analytics.get("average_score", 0) or 0
        compliance_rate = compliance_analytics.get("compliance_rate", 0) or 0
        cert_rate = cert_analytics.get("active_rate", 0) or 0
        nc_resolution_rate = nc_analytics.get("resolution_rate", 0) or 0
        
        overall_qa_score = (audit_score * 0.3 + compliance_rate * 0.3 + cert_rate * 0.2 + nc_resolution_rate * 0.2)
        
        # Risk assessment
        risk_factors = []
        if audit_score < 70:
            risk_factors.append("Low audit scores indicate quality issues")
        if compliance_rate < 90:
            risk_factors.append("Compliance gaps present regulatory risks")
        if cert_rate < 95:
            risk_factors.append("Expired certifications affect operational capability")
        if nc_analytics.get("overdue_nonconformities", 0) > 0:
            risk_factors.append("Overdue non-conformities require immediate attention")
        
        return {
            "report_type": "overall_qa_report",
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "overall_qa_score": round(overall_qa_score, 2),
            "audit_summary": audit_analytics,
            "nonconformity_summary": nc_analytics,
            "compliance_summary": compliance_analytics,
            "certification_summary": cert_analytics,
            "risk_factors": risk_factors,
            "recommendations": self._generate_overall_recommendations(
                audit_analytics, nc_analytics, compliance_analytics, cert_analytics
            ),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _generate_audit_recommendations(self, audits: List[QualityAudit]) -> List[str]:
        """Generate audit-specific recommendations"""
        recommendations = []
        
        if not audits:
            return ["No audit data available for analysis"]
        
        completed_audits = [a for a in audits if a.status == AuditStatus.COMPLETED and a.score]
        if completed_audits:
            avg_score = sum(a.score for a in completed_audits) / len(completed_audits)
            if avg_score < 70:
                recommendations.append("Average audit scores are below target - review quality processes")
            elif avg_score > 90:
                recommendations.append("Excellent audit performance - consider sharing best practices")
        
        overdue_audits = [a for a in audits if a.is_overdue()]
        if len(overdue_audits) > len(audits) * 0.1:  # More than 10% overdue
            recommendations.append("High percentage of overdue audits - review scheduling and resources")
        
        # Entity type analysis
        entity_scores = {}
        for audit in completed_audits:
            if audit.entity_type not in entity_scores:
                entity_scores[audit.entity_type] = []
            entity_scores[audit.entity_type].append(audit.score)
        
        for entity_type, scores in entity_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 75:
                recommendations.append(f"{entity_type} audits show lower performance - focus improvement efforts")
        
        return recommendations or ["Audit performance is meeting targets"]
    
    def _generate_nc_recommendations(self, nonconformities: List[NonConformity]) -> List[str]:
        """Generate non-conformity specific recommendations"""
        recommendations = []
        
        if not nonconformities:
            return ["No non-conformity data available for analysis"]
        
        # Severity analysis
        critical_ncs = [nc for nc in nonconformities if nc.severity == Severity.CRITICAL]
        if len(critical_ncs) > 0:
            recommendations.append(f"{len(critical_ncs)} critical non-conformities require immediate management attention")
        
        # Resolution analysis
        overdue_ncs = [nc for nc in nonconformities if nc.is_overdue()]
        if len(overdue_ncs) > 0:
            recommendations.append(f"{len(overdue_ncs)} overdue non-conformities need urgent resolution")
        
        # Root cause analysis
        root_causes = {}
        for nc in nonconformities:
            if nc.root_cause:
                root_causes[nc.root_cause] = root_causes.get(nc.root_cause, 0) + 1
        
        if root_causes:
            most_common = max(root_causes.items(), key=lambda x: x[1])
            if most_common[1] > len(nonconformities) * 0.2:  # More than 20%
                recommendations.append(f"'{most_common[0]}' is a recurring root cause - implement systematic prevention")
        
        return recommendations or ["Non-conformity management is effective"]
    
    def _generate_compliance_recommendations(self, requirements: List[ComplianceRequirement]) -> List[str]:
        """Generate compliance-specific recommendations"""
        recommendations = []
        
        if not requirements:
            return ["No compliance requirements defined"]
        
        expired_reqs = [r for r in requirements if r.status == ComplianceStatus.EXPIRED]
        if expired_reqs:
            recommendations.append(f"{len(expired_reqs)} compliance requirements have expired - immediate action required")
        
        pending_reqs = [r for r in requirements if r.status == ComplianceStatus.PENDING]
        if len(pending_reqs) > len(requirements) * 0.1:  # More than 10%
            recommendations.append("High number of pending compliance items - review resource allocation")
        
        # ComplianceDomain analysis
        domain_status = {}
        for req in requirements:
            if req.domain not in domain_status:
                domain_status[req.domain] = {"total": 0, "met": 0}
            domain_status[req.domain]["total"] += 1
            if req.status == ComplianceStatus.MET:
                domain_status[req.domain]["met"] += 1
        
        for domain, status in domain_status.items():
            compliance_rate = status["met"] / status["total"] * 100
            if compliance_rate < 90:
                recommendations.append(f"{domain} compliance is below 90% - prioritize this domain")
        
        return recommendations or ["Compliance management is effective"]
    
    def _generate_certification_recommendations(self, certifications: List[Certification]) -> List[str]:
        """Generate certification-specific recommendations"""
        recommendations = []
        
        if not certifications:
            return ["No certifications tracked"]
        
        expired_certs = [c for c in certifications if c.status == CertificationStatus.EXPIRED]
        if expired_certs:
            recommendations.append(f"{len(expired_certs)} certifications have expired - renew immediately")
        
        # Expiring soon
        alert_date = date.today() + timedelta(days=60)
        expiring_soon = [c for c in certifications if c.expiry_date and c.expiry_date <= alert_date and c.status == CertificationStatus.ACTIVE]
        if expiring_soon:
            recommendations.append(f"{len(expiring_soon)} certifications expire within 60 days - plan renewals")
        
        return recommendations or ["Certification management is up to date"]
    
    def _generate_overall_recommendations(
        self,
        audit_analytics: Dict[str, Any],
        nc_analytics: Dict[str, Any],
        compliance_analytics: Dict[str, Any],
        cert_analytics: Dict[str, Any]
    ) -> List[str]:
        """Generate overall QA recommendations"""
        recommendations = []
        
        # Priority recommendations based on scores
        if audit_analytics.get("average_score", 0) < 70:
            recommendations.append("PRIORITY: Audit scores below target - implement quality improvement program")
        
        if nc_analytics.get("overdue_nonconformities", 0) > 0:
            recommendations.append("URGENT: Resolve overdue non-conformities to prevent escalation")
        
        if compliance_analytics.get("compliance_rate", 0) < 90:
            recommendations.append("CRITICAL: Compliance gaps present regulatory risks - immediate action required")
        
        if cert_analytics.get("expired_certifications", 0) > 0:
            recommendations.append("IMMEDIATE: Expired certifications affect operational capability")
        
        # Strategic recommendations
        if audit_analytics.get("completion_rate", 0) < 95:
            recommendations.append("Improve audit scheduling and completion rates")
        
        if nc_analytics.get("resolution_rate", 0) < 85:
            recommendations.append("Enhance non-conformity resolution processes")
        
        return recommendations or ["Overall QA performance is satisfactory"]