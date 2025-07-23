"""
Database models for the HR microservice
"""
from .employee import Employee, Gender, MaritalStatus, EmploymentType, ContractType, EmployeeStatus
from .job_application import JobApplication, ApplicationSource, ApplicationStage, Priority
from .training_program import TrainingProgram, TrainingCategory, TrainingStatus, DeliveryMethod
from .employee_training import EmployeeTraining, AttendanceStatus, CompletionStatus
from .employee_document import EmployeeDocument, DocumentType, DocumentStatus

__all__ = [
    "Employee", "Gender", "MaritalStatus", "EmploymentType", "ContractType", "EmployeeStatus",
    "JobApplication", "ApplicationSource", "ApplicationStage", "Priority",
    "TrainingProgram", "TrainingCategory", "TrainingStatus", "DeliveryMethod",
    "EmployeeTraining", "AttendanceStatus", "CompletionStatus",
    "EmployeeDocument", "DocumentType", "DocumentStatus"
]