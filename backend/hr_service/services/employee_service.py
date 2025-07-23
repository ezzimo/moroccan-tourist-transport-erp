"""
Employee service for employee management operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.employee import Employee, EmployeeStatus
from models.employee_training import EmployeeTraining
from models.employee_document import EmployeeDocument
from schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeSummary, 
    EmployeeSearch, EmployeeTermination
)
from utils.pagination import PaginationParams, paginate_query
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import redis
import uuid


class EmployeeService:
    """Service for handling employee operations"""
    
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
    
    async def create_employee(self, employee_data: EmployeeCreate) -> EmployeeResponse:
        """Create a new employee"""
        # Check if employee ID already exists
        statement = select(Employee).where(Employee.employee_id == employee_data.employee_id)
        existing_employee = self.session.exec(statement).first()
        
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already exists"
            )
        
        # Check if national ID already exists
        national_id_stmt = select(Employee).where(Employee.national_id == employee_data.national_id)
        existing_national_id = self.session.exec(national_id_stmt).first()
        
        if existing_national_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="National ID already exists"
            )
        
        # Check if email already exists
        email_stmt = select(Employee).where(Employee.email == employee_data.email)
        existing_email = self.session.exec(email_stmt).first()
        
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Calculate probation end date
        from config import settings
        probation_end_date = employee_data.hire_date + timedelta(days=settings.probation_period_months * 30)
        
        # Create employee
        employee = Employee(
            **employee_data.model_dump(),
            probation_end_date=probation_end_date
        )
        
        self.session.add(employee)
        self.session.commit()
        self.session.refresh(employee)
        
        return self._create_employee_response(employee)
    
    async def get_employee(self, employee_id: uuid.UUID) -> EmployeeResponse:
        """Get employee by ID"""
        statement = select(Employee).where(Employee.id == employee_id)
        employee = self.session.exec(statement).first()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        return self._create_employee_response(employee)
    
    async def get_employees(
        self, 
        pagination: PaginationParams,
        search: Optional[EmployeeSearch] = None
    ) -> Tuple[List[EmployeeResponse], int]:
        """Get list of employees with optional search"""
        query = select(Employee)
        
        # Apply search filters
        if search:
            conditions = []
            
            if search.query:
                search_term = f"%{search.query}%"
                conditions.append(
                    or_(
                        Employee.full_name.ilike(search_term),
                        Employee.employee_id.ilike(search_term),
                        Employee.email.ilike(search_term),
                        Employee.national_id.ilike(search_term)
                    )
                )
            
            if search.department:
                conditions.append(Employee.department.ilike(f"%{search.department}%"))
            
            if search.position:
                conditions.append(Employee.position.ilike(f"%{search.position}%"))
            
            if search.employment_type:
                conditions.append(Employee.employment_type == search.employment_type)
            
            if search.contract_type:
                conditions.append(Employee.contract_type == search.contract_type)
            
            if search.status:
                conditions.append(Employee.status == search.status)
            
            if search.manager_id:
                conditions.append(Employee.manager_id == search.manager_id)
            
            if search.hire_date_from:
                conditions.append(Employee.hire_date >= search.hire_date_from)
            
            if search.hire_date_to:
                conditions.append(Employee.hire_date <= search.hire_date_to)
            
            if search.is_active is not None:
                conditions.append(Employee.is_active == search.is_active)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Order by hire date (newest first)
        query = query.order_by(Employee.hire_date.desc())
        
        employees, total = paginate_query(self.session, query, pagination)
        
        return [self._create_employee_response(employee) for employee in employees], total
    
    async def update_employee(self, employee_id: uuid.UUID, employee_data: EmployeeUpdate) -> EmployeeResponse:
        """Update employee information"""
        statement = select(Employee).where(Employee.id == employee_id)
        employee = self.session.exec(statement).first()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Check email uniqueness if being updated
        if employee_data.email and employee_data.email != employee.email:
            email_stmt = select(Employee).where(Employee.email == employee_data.email)
            existing_email = self.session.exec(email_stmt).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        # Update fields
        update_data = employee_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(employee, field, value)
        
        employee.updated_at = datetime.utcnow()
        
        self.session.add(employee)
        self.session.commit()
        self.session.refresh(employee)
        
        return self._create_employee_response(employee)
    
    async def terminate_employee(
        self, 
        employee_id: uuid.UUID, 
        termination_data: EmployeeTermination,
        terminated_by: uuid.UUID
    ) -> EmployeeResponse:
        """Terminate an employee"""
        statement = select(Employee).where(Employee.id == employee_id)
        employee = self.session.exec(statement).first()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        if employee.status == EmployeeStatus.TERMINATED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee is already terminated"
            )
        
        # Update employee status
        employee.status = EmployeeStatus.TERMINATED
        employee.is_active = False
        employee.termination_date = datetime.combine(termination_data.termination_date, datetime.min.time())
        employee.updated_at = datetime.utcnow()
        
        # Add termination notes
        termination_note = f"Terminated on {termination_data.termination_date}: {termination_data.reason}"
        if termination_data.notes:
            termination_note += f"\nAdditional notes: {termination_data.notes}"
        
        if employee.notes:
            employee.notes += f"\n\n{termination_note}"
        else:
            employee.notes = termination_note
        
        self.session.add(employee)
        self.session.commit()
        self.session.refresh(employee)
        
        return self._create_employee_response(employee)
    
    async def delete_employee(self, employee_id: uuid.UUID) -> dict:
        """Delete employee (soft delete)"""
        statement = select(Employee).where(Employee.id == employee_id)
        employee = self.session.exec(statement).first()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        employee.is_active = False
        employee.updated_at = datetime.utcnow()
        
        self.session.add(employee)
        self.session.commit()
        
        return {"message": "Employee deactivated successfully"}
    
    async def get_employee_summary(self, employee_id: uuid.UUID) -> EmployeeSummary:
        """Get comprehensive employee summary with statistics"""
        statement = select(Employee).where(Employee.id == employee_id)
        employee = self.session.exec(statement).first()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Get training statistics
        training_stmt = select(EmployeeTraining).where(EmployeeTraining.employee_id == employee_id)
        trainings = self.session.exec(training_stmt).all()
        
        completed_trainings = len([t for t in trainings if t.completion_status.value == "Completed"])
        pending_trainings = len([t for t in trainings if t.completion_status.value in ["Not Started", "In Progress"]])
        certificates_count = len([t for t in trainings if t.certificate_issued])
        
        # Calculate total training hours
        total_training_hours = 0
        for training in trainings:
            if training.training_program:
                total_training_hours += training.training_program.duration_hours
        
        # Get documents count
        documents_stmt = select(func.count(EmployeeDocument.id)).where(
            EmployeeDocument.employee_id == employee_id
        )
        documents_count = self.session.exec(documents_stmt).one()
        
        # Get manager name
        manager_name = None
        if employee.manager:
            manager_name = employee.manager.full_name
        
        # Get direct reports count
        direct_reports_stmt = select(func.count(Employee.id)).where(
            Employee.manager_id == employee_id,
            Employee.is_active == True
        )
        direct_reports_count = self.session.exec(direct_reports_stmt).one()
        
        # Get training dates
        last_training_date = None
        next_training_date = None
        
        if trainings:
            completed_trainings_with_dates = [
                t for t in trainings 
                if t.completion_date and t.completion_status.value == "Completed"
            ]
            if completed_trainings_with_dates:
                last_training_date = max(t.completion_date for t in completed_trainings_with_dates)
        
        # Create summary response
        base_response = self._create_employee_response(employee)
        
        return EmployeeSummary(
            **base_response.model_dump(),
            total_training_hours=total_training_hours,
            completed_trainings=completed_trainings,
            pending_trainings=pending_trainings,
            certificates_count=certificates_count,
            documents_count=documents_count,
            manager_name=manager_name,
            direct_reports_count=direct_reports_count,
            last_training_date=last_training_date,
            next_training_date=next_training_date
        )
    
    async def get_employees_by_department(self, department: str) -> List[EmployeeResponse]:
        """Get all employees in a department"""
        statement = select(Employee).where(
            Employee.department.ilike(f"%{department}%"),
            Employee.is_active == True
        ).order_by(Employee.full_name)
        
        employees = self.session.exec(statement).all()
        
        return [self._create_employee_response(employee) for employee in employees]
    
    async def get_direct_reports(self, manager_id: uuid.UUID) -> List[EmployeeResponse]:
        """Get direct reports for a manager"""
        statement = select(Employee).where(
            Employee.manager_id == manager_id,
            Employee.is_active == True
        ).order_by(Employee.full_name)
        
        employees = self.session.exec(statement).all()
        
        return [self._create_employee_response(employee) for employee in employees]
    
    async def get_expiring_contracts(self, days_ahead: int = 30) -> List[EmployeeResponse]:
        """Get employees with contracts expiring soon"""
        cutoff_date = date.today() + timedelta(days=days_ahead)
        
        statement = select(Employee).where(
            Employee.contract_end_date <= cutoff_date,
            Employee.contract_end_date >= date.today(),
            Employee.is_active == True
        ).order_by(Employee.contract_end_date)
        
        employees = self.session.exec(statement).all()
        
        return [self._create_employee_response(employee) for employee in employees]
    
    async def bulk_update_employees(
        self, 
        employee_ids: List[uuid.UUID], 
        update_data: EmployeeUpdate
    ) -> dict:
        """Bulk update multiple employees"""
        statement = select(Employee).where(Employee.id.in_(employee_ids))
        employees = self.session.exec(statement).all()
        
        if len(employees) != len(employee_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more employees not found"
            )
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_count = 0
        
        for employee in employees:
            for field, value in update_dict.items():
                setattr(employee, field, value)
            
            employee.updated_at = datetime.utcnow()
            self.session.add(employee)
            updated_count += 1
        
        self.session.commit()
        
        return {
            "message": f"Successfully updated {updated_count} employees",
            "updated_count": updated_count
        }
    
    def _create_employee_response(self, employee: Employee) -> EmployeeResponse:
        """Create employee response with calculated fields"""
        return EmployeeResponse(
            id=employee.id,
            employee_id=employee.employee_id,
            full_name=employee.full_name,
            national_id=employee.national_id,
            gender=employee.gender,
            birth_date=employee.birth_date,
            marital_status=employee.marital_status,
            email=employee.email,
            phone=employee.phone,
            address=employee.address,
            emergency_contact_name=employee.emergency_contact_name,
            emergency_contact_phone=employee.emergency_contact_phone,
            department=employee.department,
            position=employee.position,
            employment_type=employee.employment_type,
            contract_type=employee.contract_type,
            hire_date=employee.hire_date,
            contract_start_date=employee.contract_start_date,
            contract_end_date=employee.contract_end_date,
            base_salary=employee.base_salary,
            social_security_number=employee.social_security_number,
            tax_id=employee.tax_id,
            bank_account=employee.bank_account,
            manager_id=employee.manager_id,
            notes=employee.notes,
            status=employee.status,
            probation_end_date=employee.probation_end_date,
            is_active=employee.is_active,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
            termination_date=employee.termination_date,
            age=employee.get_age(),
            years_of_service=employee.get_years_of_service(),
            is_on_probation=employee.is_on_probation(),
            display_name=employee.get_display_name(),
            monthly_salary=employee.calculate_monthly_salary()
        )