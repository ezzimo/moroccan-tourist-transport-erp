"""
Employee management routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from database import get_session, get_redis
from services.employee_service import EmployeeService
from schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeSummary,
    EmployeeSearch, EmployeeTermination
)
from models.employee import EmploymentType, ContractType, EmployeeStatus
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional, Dict, Any
import redis
import uuid


router = APIRouter(prefix="/employees", tags=["Employee Management"])


@router.post("/", response_model=EmployeeResponse)
async def create_employee(
    employee_data: EmployeeCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "create", "employees"))
):
    """Create a new employee"""
    employee_service = EmployeeService(session, redis_client)
    return await employee_service.create_employee(employee_data)


@router.get("/", response_model=PaginatedResponse[EmployeeResponse])
async def get_employees(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    department: Optional[str] = Query(None, description="Filter by department"),
    position: Optional[str] = Query(None, description="Filter by position"),
    employment_type: Optional[EmploymentType] = Query(None, description="Filter by employment type"),
    contract_type: Optional[ContractType] = Query(None, description="Filter by contract type"),
    status: Optional[EmployeeStatus] = Query(None, description="Filter by status"),
    manager_id: Optional[uuid.UUID] = Query(None, description="Filter by manager"),
    hire_date_from: Optional[str] = Query(None, description="Filter by hire date from (YYYY-MM-DD)"),
    hire_date_to: Optional[str] = Query(None, description="Filter by hire date to (YYYY-MM-DD)"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "employees"))
):
    """Get list of employees with optional search and filters"""
    employee_service = EmployeeService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([query, department, position, employment_type, contract_type, status, 
            manager_id, hire_date_from, hire_date_to, is_active is not None]):
        from datetime import datetime
        
        hire_date_from_parsed = None
        hire_date_to_parsed = None
        
        if hire_date_from:
            try:
                hire_date_from_parsed = datetime.strptime(hire_date_from, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid hire_date_from format. Use YYYY-MM-DD"
                )
        
        if hire_date_to:
            try:
                hire_date_to_parsed = datetime.strptime(hire_date_to, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid hire_date_to format. Use YYYY-MM-DD"
                )
        
        search = EmployeeSearch(
            query=query,
            department=department,
            position=position,
            employment_type=employment_type,
            contract_type=contract_type,
            status=status,
            manager_id=manager_id,
            hire_date_from=hire_date_from_parsed,
            hire_date_to=hire_date_to_parsed,
            is_active=is_active
        )
    
    employees, total = await employee_service.get_employees(pagination, search)
    
    return PaginatedResponse.create(
        items=employees,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "employees"))
):
    """Get employee by ID"""
    employee_service = EmployeeService(session, redis_client)
    return await employee_service.get_employee(employee_id)


@router.get("/{employee_id}/summary", response_model=EmployeeSummary)
async def get_employee_summary(
    employee_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "employees"))
):
    """Get comprehensive employee summary"""
    employee_service = EmployeeService(session, redis_client)
    return await employee_service.get_employee_summary(employee_id)


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: uuid.UUID,
    employee_data: EmployeeUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "update", "employees"))
):
    """Update employee information"""
    employee_service = EmployeeService(session, redis_client)
    return await employee_service.update_employee(employee_id, employee_data)


@router.post("/{employee_id}/terminate", response_model=EmployeeResponse)
async def terminate_employee(
    employee_id: uuid.UUID,
    termination_data: EmployeeTermination,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "update", "employees"))
):
    """Terminate an employee"""
    employee_service = EmployeeService(session, redis_client)
    return await employee_service.terminate_employee(employee_id, termination_data, current_user.user_id)


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "delete", "employees"))
):
    """Delete employee (soft delete)"""
    employee_service = EmployeeService(session, redis_client)
    return await employee_service.delete_employee(employee_id)


@router.get("/department/{department}", response_model=List[EmployeeResponse])
async def get_employees_by_department(
    department: str,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "employees"))
):
    """Get all employees in a department"""
    employee_service = EmployeeService(session, redis_client)
    return await employee_service.get_employees_by_department(department)


@router.get("/manager/{manager_id}", response_model=List[EmployeeResponse])
async def get_direct_reports(
    manager_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "employees"))
):
    """Get direct reports for a manager"""
    employee_service = EmployeeService(session, redis_client)
    return await employee_service.get_direct_reports(manager_id)


@router.get("/contracts/expiring", response_model=List[EmployeeResponse])
async def get_expiring_contracts(
    days_ahead: int = Query(30, ge=1, le=365, description="Days ahead to check"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "employees"))
):
    """Get employees with contracts expiring soon"""
    employee_service = EmployeeService(session, redis_client)
    return await employee_service.get_expiring_contracts(days_ahead)


@router.post("/bulk-update")
async def bulk_update_employees(
    employee_ids: List[uuid.UUID],
    update_data: EmployeeUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "update", "employees"))
):
    """Bulk update multiple employees"""
    employee_service = EmployeeService(session, redis_client)
    return await employee_service.bulk_update_employees(employee_ids, update_data)