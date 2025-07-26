"""
Analytics service for HR metrics, KPIs, and reporting
"""
from sqlmodel import Session, select, and_, func
from models.employee import Employee, EmployeeStatus
from models.job_application import JobApplication, ApplicationStage
from models.training_program import TrainingProgram, TrainingStatus
from models.employee_training import EmployeeTraining
from models.employee_document import EmployeeDocument, DocumentStatus
from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for HR analytics, KPIs, and reporting"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def get_hr_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive HR dashboard metrics
        
        Returns:
            HR dashboard data with key metrics
        """
        # Employee metrics
        total_employees = self.session.exec(select(func.count(Employee.id))).first()
        active_employees = self.session.exec(
            select(func.count(Employee.id)).where(Employee.status == EmployeeStatus.ACTIVE)
        ).first()
        
        # Recent hires (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_hires = self.session.exec(
            select(func.count(Employee.id)).where(Employee.start_date >= thirty_days_ago)
        ).first()
        
        # Recruitment metrics
        total_applications = self.session.exec(select(func.count(JobApplication.id))).first()
        pending_applications = self.session.exec(
            select(func.count(JobApplication.id)).where(
                JobApplication.stage.in_([ApplicationStage.SCREENING, ApplicationStage.INTERVIEW])
            )
        ).first()
        
        # Training metrics
        total_trainings = self.session.exec(select(func.count(EmployeeTraining.id))).first()
        completed_trainings = self.session.exec(
            select(func.count(EmployeeTraining.id)).where(
                EmployeeTraining.status == TrainingStatus.COMPLETED
            )
        ).first()
        
        # Document compliance
        pending_documents = self.session.exec(
            select(func.count(EmployeeDocument.id)).where(
                EmployeeDocument.status == DocumentStatus.PENDING
            )
        ).first()
        
        return {
            "employee_metrics": {
                "total_employees": total_employees or 0,
                "active_employees": active_employees or 0,
                "recent_hires": recent_hires or 0,
                "employee_growth_rate": self._calculate_growth_rate("employees")
            },
            "recruitment_metrics": {
                "total_applications": total_applications or 0,
                "pending_applications": pending_applications or 0,
                "hire_rate": await self._calculate_hire_rate()
            },
            "training_metrics": {
                "total_trainings": total_trainings or 0,
                "completed_trainings": completed_trainings or 0,
                "completion_rate": completed_trainings / total_trainings * 100 if total_trainings else 0
            },
            "compliance_metrics": {
                "pending_documents": pending_documents or 0,
                "expiring_documents": await self._count_expiring_documents()
            }
        }
    
    async def get_employee_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get detailed employee analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Employee analytics data
        """
        query = select(Employee)
        
        # Apply date filters
        conditions = []
        if start_date:
            conditions.append(Employee.start_date >= start_date)
        if end_date:
            conditions.append(Employee.start_date <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        employees = self.session.exec(query).all()
        
        # Demographics analysis
        by_gender = {}
        by_employment_type = {}
        by_department = {}
        by_status = {}
        
        total_salary = Decimal('0')
        salary_count = 0
        
        for employee in employees:
            # Gender distribution
            gender = getattr(employee, 'gender', 'Unknown')
            by_gender[gender] = by_gender.get(gender, 0) + 1
            
            # Employment type
            emp_type = employee.employment_type.value
            by_employment_type[emp_type] = by_employment_type.get(emp_type, 0) + 1
            
            # Department
            department = getattr(employee, 'department', 'Unknown')
            by_department[department] = by_department.get(department, 0) + 1
            
            # Status
            status = employee.status.value
            by_status[status] = by_status.get(status, 0) + 1
            
            # Salary analysis
            if hasattr(employee, 'salary') and employee.salary:
                total_salary += employee.salary
                salary_count += 1
        
        # Calculate averages
        average_salary = float(total_salary / salary_count) if salary_count > 0 else 0
        
        # Tenure analysis
        tenure_analysis = await self._analyze_employee_tenure(employees)
        
        return {
            "total_employees": len(employees),
            "demographics": {
                "by_gender": by_gender,
                "by_employment_type": by_employment_type,
                "by_department": by_department,
                "by_status": by_status
            },
            "compensation": {
                "average_salary": average_salary,
                "total_payroll": float(total_salary)
            },
            "tenure_analysis": tenure_analysis,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def get_turnover_analysis(
        self,
        months: int = 12
    ) -> Dict[str, Any]:
        """Get employee turnover analysis
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Turnover analysis data
        """
        start_date = date.today() - timedelta(days=months * 30)
        
        # Get all employees who left during the period
        terminated_employees = self.session.exec(
            select(Employee).where(
                and_(
                    Employee.status.in_([EmployeeStatus.TERMINATED, EmployeeStatus.RESIGNED]),
                    Employee.end_date >= start_date if hasattr(Employee, 'end_date') else True
                )
            )
        ).all()
        
        # Get average employee count during the period
        total_employees = self.session.exec(select(func.count(Employee.id))).first() or 0
        
        # Calculate turnover rate
        turnover_count = len(terminated_employees)
        turnover_rate = turnover_count / total_employees * 100 if total_employees > 0 else 0
        
        # Analyze reasons for leaving
        termination_reasons = {}
        voluntary_vs_involuntary = {"voluntary": 0, "involuntary": 0}
        
        for employee in terminated_employees:
            # This would come from termination records in a real system
            reason = getattr(employee, 'termination_reason', 'Unknown')
            termination_reasons[reason] = termination_reasons.get(reason, 0) + 1
            
            # Classify as voluntary or involuntary
            if employee.status == EmployeeStatus.RESIGNED:
                voluntary_vs_involuntary["voluntary"] += 1
            else:
                voluntary_vs_involuntary["involuntary"] += 1
        
        # Department-wise turnover
        department_turnover = {}
        for employee in terminated_employees:
            dept = getattr(employee, 'department', 'Unknown')
            department_turnover[dept] = department_turnover.get(dept, 0) + 1
        
        # Monthly turnover trend
        monthly_turnover = await self._calculate_monthly_turnover(months)
        
        return {
            "turnover_rate": turnover_rate,
            "turnover_count": turnover_count,
            "total_employees": total_employees,
            "termination_analysis": {
                "reasons": termination_reasons,
                "voluntary_vs_involuntary": voluntary_vs_involuntary,
                "by_department": department_turnover
            },
            "monthly_trend": monthly_turnover,
            "period_months": months
        }
    
    async def get_recruitment_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get recruitment analytics and funnel analysis
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Recruitment analytics data
        """
        query = select(JobApplication)
        
        # Apply date filters
        conditions = []
        if start_date:
            conditions.append(JobApplication.created_at >= start_date)
        if end_date:
            conditions.append(JobApplication.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        applications = self.session.exec(query).all()
        
        # Funnel analysis
        funnel_data = {}
        for stage in ApplicationStage:
            count = len([a for a in applications if a.stage == stage])
            funnel_data[stage.value] = count
        
        # Conversion rates
        total_applications = len(applications)
        hired_count = funnel_data.get(ApplicationStage.HIRED.value, 0)
        
        conversion_rates = {}
        if total_applications > 0:
            conversion_rates["application_to_hire"] = hired_count / total_applications * 100
            
            interview_count = funnel_data.get(ApplicationStage.INTERVIEW.value, 0)
            if interview_count > 0:
                conversion_rates["interview_to_hire"] = hired_count / interview_count * 100
        
        # Source effectiveness
        source_analysis = {}
        for app in applications:
            source = app.source.value
            if source not in source_analysis:
                source_analysis[source] = {"total": 0, "hired": 0}
            
            source_analysis[source]["total"] += 1
            if app.stage == ApplicationStage.HIRED:
                source_analysis[source]["hired"] += 1
        
        # Calculate source conversion rates
        for source_data in source_analysis.values():
            if source_data["total"] > 0:
                source_data["conversion_rate"] = source_data["hired"] / source_data["total"] * 100
        
        # Time to hire analysis
        hired_applications = [a for a in applications if a.stage == ApplicationStage.HIRED]
        time_to_hire_data = []
        
        for app in hired_applications:
            if app.updated_at:
                days = (app.updated_at.date() - app.created_at.date()).days
                time_to_hire_data.append(days)
        
        avg_time_to_hire = sum(time_to_hire_data) / len(time_to_hire_data) if time_to_hire_data else 0
        
        # Position analysis
        position_analysis = {}
        for app in applications:
            position = app.position_applied
            if position not in position_analysis:
                position_analysis[position] = {"applications": 0, "hired": 0}
            
            position_analysis[position]["applications"] += 1
            if app.stage == ApplicationStage.HIRED:
                position_analysis[position]["hired"] += 1
        
        return {
            "total_applications": total_applications,
            "hired_count": hired_count,
            "funnel_analysis": funnel_data,
            "conversion_rates": conversion_rates,
            "source_effectiveness": source_analysis,
            "time_to_hire": {
                "average_days": avg_time_to_hire,
                "data_points": len(time_to_hire_data)
            },
            "position_analysis": position_analysis,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def get_training_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get training analytics and ROI analysis
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Training analytics data
        """
        # Get training programs
        program_query = select(TrainingProgram)
        if start_date:
            program_query = program_query.where(TrainingProgram.start_date >= start_date)
        if end_date:
            program_query = program_query.where(TrainingProgram.end_date <= end_date)
        
        programs = self.session.exec(program_query).all()
        
        # Get employee training records
        training_query = select(EmployeeTraining)
        if start_date:
            training_query = training_query.where(EmployeeTraining.created_at >= start_date)
        if end_date:
            training_query = training_query.where(EmployeeTraining.created_at <= end_date)
        
        trainings = self.session.exec(training_query).all()
        
        # Calculate metrics
        total_programs = len(programs)
        total_trainings = len(trainings)
        completed_trainings = len([t for t in trainings if t.status == TrainingStatus.COMPLETED])
        
        # Completion rate
        completion_rate = completed_trainings / total_trainings * 100 if total_trainings > 0 else 0
        
        # Average scores
        completed_with_scores = [t for t in trainings if t.evaluation_score is not None]
        average_score = sum(t.evaluation_score for t in completed_with_scores) / len(completed_with_scores) if completed_with_scores else 0
        
        # Training costs
        total_cost = sum(p.cost for p in programs if p.cost)
        cost_per_employee = total_cost / total_trainings if total_trainings > 0 else 0
        
        # Category analysis
        category_analysis = {}
        for program in programs:
            category = program.category.value
            if category not in category_analysis:
                category_analysis[category] = {
                    "programs": 0,
                    "participants": 0,
                    "completed": 0,
                    "cost": 0
                }
            
            category_analysis[category]["programs"] += 1
            category_analysis[category]["cost"] += program.cost or 0
            
            # Count participants for this program
            program_trainings = [t for t in trainings if t.training_program_id == program.id]
            category_analysis[category]["participants"] += len(program_trainings)
            category_analysis[category]["completed"] += len([
                t for t in program_trainings if t.status == TrainingStatus.COMPLETED
            ])
        
        # Calculate completion rates for each category
        for cat_data in category_analysis.values():
            if cat_data["participants"] > 0:
                cat_data["completion_rate"] = cat_data["completed"] / cat_data["participants"] * 100
        
        # Training effectiveness (simplified ROI calculation)
        effectiveness_score = await self._calculate_training_effectiveness(trainings)
        
        return {
            "overview": {
                "total_programs": total_programs,
                "total_trainings": total_trainings,
                "completed_trainings": completed_trainings,
                "completion_rate": completion_rate,
                "average_score": average_score
            },
            "financial": {
                "total_cost": total_cost,
                "cost_per_employee": cost_per_employee,
                "roi_estimate": effectiveness_score
            },
            "category_analysis": category_analysis,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def get_compliance_report(self) -> Dict[str, Any]:
        """Get HR compliance report
        
        Returns:
            Compliance report data
        """
        # Document compliance
        total_documents = self.session.exec(select(func.count(EmployeeDocument.id))).first() or 0
        approved_documents = self.session.exec(
            select(func.count(EmployeeDocument.id)).where(
                EmployeeDocument.status == DocumentStatus.APPROVED
            )
        ).first() or 0
        
        # Expiring documents
        thirty_days = date.today() + timedelta(days=30)
        expiring_documents = self.session.exec(
            select(func.count(EmployeeDocument.id)).where(
                and_(
                    EmployeeDocument.expiry_date.is_not(None),
                    EmployeeDocument.expiry_date <= thirty_days,
                    EmployeeDocument.expiry_date > date.today()
                )
            )
        ).first() or 0
        
        # Training compliance
        mandatory_programs = self.session.exec(
            select(TrainingProgram).where(TrainingProgram.mandatory == True)
        ).all()
        
        training_compliance = {}
        for program in mandatory_programs:
            total_employees = self.session.exec(select(func.count(Employee.id))).first() or 0
            completed_count = self.session.exec(
                select(func.count(EmployeeTraining.id)).where(
                    and_(
                        EmployeeTraining.training_program_id == program.id,
                        EmployeeTraining.status == TrainingStatus.COMPLETED
                    )
                )
            ).first() or 0
            
            compliance_rate = completed_count / total_employees * 100 if total_employees > 0 else 0
            training_compliance[program.title] = {
                "required": total_employees,
                "completed": completed_count,
                "compliance_rate": compliance_rate
            }
        
        # Contract compliance
        active_employees = self.session.exec(
            select(Employee).where(Employee.status == EmployeeStatus.ACTIVE)
        ).all()
        
        contract_issues = []
        for employee in active_employees:
            # Check for missing contracts (this would be more sophisticated in reality)
            employee_docs = self.session.exec(
                select(EmployeeDocument).where(
                    and_(
                        EmployeeDocument.employee_id == employee.id,
                        EmployeeDocument.document_type == "CONTRACT"
                    )
                )
            ).all()
            
            if not employee_docs:
                contract_issues.append({
                    "employee_id": str(employee.id),
                    "employee_name": employee.full_name,
                    "issue": "Missing contract"
                })
        
        return {
            "document_compliance": {
                "total_documents": total_documents,
                "approved_documents": approved_documents,
                "approval_rate": approved_documents / total_documents * 100 if total_documents > 0 else 0,
                "expiring_documents": expiring_documents
            },
            "training_compliance": training_compliance,
            "contract_compliance": {
                "total_employees": len(active_employees),
                "contract_issues": len(contract_issues),
                "issues_details": contract_issues[:10]  # Limit to first 10 for brevity
            },
            "overall_compliance_score": await self._calculate_overall_compliance_score()
        }
    
    # Helper methods
    
    def _calculate_growth_rate(self, metric_type: str) -> float:
        """Calculate growth rate for a metric"""
        # This is a simplified calculation - in reality, you'd compare periods
        current_month = date.today().replace(day=1)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        if metric_type == "employees":
            current_count = self.session.exec(
                select(func.count(Employee.id)).where(Employee.start_date < current_month)
            ).first() or 0
            
            last_month_count = self.session.exec(
                select(func.count(Employee.id)).where(Employee.start_date < last_month)
            ).first() or 0
            
            if last_month_count > 0:
                return (current_count - last_month_count) / last_month_count * 100
        
        return 0.0
    
    async def _calculate_hire_rate(self) -> float:
        """Calculate overall hire rate"""
        total_applications = self.session.exec(select(func.count(JobApplication.id))).first() or 0
        hired_applications = self.session.exec(
            select(func.count(JobApplication.id)).where(
                JobApplication.stage == ApplicationStage.HIRED
            )
        ).first() or 0
        
        return hired_applications / total_applications * 100 if total_applications > 0 else 0
    
    async def _count_expiring_documents(self) -> int:
        """Count documents expiring within 30 days"""
        alert_date = date.today() + timedelta(days=30)
        return self.session.exec(
            select(func.count(EmployeeDocument.id)).where(
                and_(
                    EmployeeDocument.expiry_date.is_not(None),
                    EmployeeDocument.expiry_date <= alert_date,
                    EmployeeDocument.expiry_date > date.today()
                )
            )
        ).first() or 0
    
    async def _analyze_employee_tenure(self, employees: List[Employee]) -> Dict[str, Any]:
        """Analyze employee tenure distribution"""
        tenure_buckets = {
            "0-1 years": 0,
            "1-3 years": 0,
            "3-5 years": 0,
            "5-10 years": 0,
            "10+ years": 0
        }
        
        total_tenure = 0
        for employee in employees:
            tenure_years = (date.today() - employee.start_date).days / 365.25
            total_tenure += tenure_years
            
            if tenure_years < 1:
                tenure_buckets["0-1 years"] += 1
            elif tenure_years < 3:
                tenure_buckets["1-3 years"] += 1
            elif tenure_years < 5:
                tenure_buckets["3-5 years"] += 1
            elif tenure_years < 10:
                tenure_buckets["5-10 years"] += 1
            else:
                tenure_buckets["10+ years"] += 1
        
        average_tenure = total_tenure / len(employees) if employees else 0
        
        return {
            "distribution": tenure_buckets,
            "average_tenure_years": average_tenure
        }
    
    async def _calculate_monthly_turnover(self, months: int) -> List[Dict[str, Any]]:
        """Calculate monthly turnover trend"""
        monthly_data = []
        
        for i in range(months):
            month_start = date.today().replace(day=1) - timedelta(days=i * 30)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # This is simplified - in reality you'd track actual termination dates
            terminated_count = self.session.exec(
                select(func.count(Employee.id)).where(
                    and_(
                        Employee.status.in_([EmployeeStatus.TERMINATED, EmployeeStatus.RESIGNED]),
                        # Would use actual termination date field
                    )
                )
            ).first() or 0
            
            monthly_data.append({
                "month": month_start.strftime("%Y-%m"),
                "terminations": terminated_count
            })
        
        return list(reversed(monthly_data))
    
    async def _calculate_training_effectiveness(self, trainings: List[EmployeeTraining]) -> float:
        """Calculate training effectiveness score"""
        if not trainings:
            return 0.0
        
        # Simplified effectiveness calculation based on completion rates and scores
        completed_trainings = [t for t in trainings if t.status == TrainingStatus.COMPLETED]
        completion_rate = len(completed_trainings) / len(trainings)
        
        # Average score factor
        scored_trainings = [t for t in completed_trainings if t.evaluation_score is not None]
        if scored_trainings:
            avg_score = sum(t.evaluation_score for t in scored_trainings) / len(scored_trainings)
            score_factor = avg_score / 100
        else:
            score_factor = 0.7  # Default assumption
        
        # Combined effectiveness score
        effectiveness = (completion_rate * 0.6 + score_factor * 0.4) * 100
        return min(100, max(0, effectiveness))
    
    async def _calculate_overall_compliance_score(self) -> float:
        """Calculate overall HR compliance score"""
        # Document compliance (30% weight)
        total_docs = self.session.exec(select(func.count(EmployeeDocument.id))).first() or 1
        approved_docs = self.session.exec(
            select(func.count(EmployeeDocument.id)).where(
                EmployeeDocument.status == DocumentStatus.APPROVED
            )
        ).first() or 0
        doc_compliance = approved_docs / total_docs
        
        # Training compliance (40% weight)
        total_trainings = self.session.exec(select(func.count(EmployeeTraining.id))).first() or 1
        completed_trainings = self.session.exec(
            select(func.count(EmployeeTraining.id)).where(
                EmployeeTraining.status == TrainingStatus.COMPLETED
            )
        ).first() or 0
        training_compliance = completed_trainings / total_trainings
        
        # Contract compliance (30% weight) - simplified
        contract_compliance = 0.9  # Assume 90% compliance
        
        overall_score = (
            doc_compliance * 0.3 +
            training_compliance * 0.4 +
            contract_compliance * 0.3
        ) * 100
        
        return min(100, max(0, overall_score))