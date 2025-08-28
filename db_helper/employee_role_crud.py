"""
Employee and Role Management CRUD Operations
"""

import bcrypt
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from db_helper.models import Employee, Role, PagePermission, RolePermission
from schemas.schemas import (
    RoleCreate, RoleUpdate, RoleResponse,
    PagePermissionCreate, PagePermissionUpdate, PagePermissionResponse,
    RolePermissionCreate, RolePermissionUpdate, RolePermissionResponse,
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    UserPermissions, PageInfo
)


class EmployeeRoleCRUD:
    # ============================================================================
    # ROLE METHODS
    # ============================================================================
    
    @staticmethod
    def create_role(db: Session, data: RoleCreate, created_by: str = None) -> RoleResponse:
        role = Role(
            name=data.name,
            description=data.description,
            is_active=data.is_active,
            created_by=created_by
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
        return db.query(Role).filter(Role.id == role_id).first()

    @staticmethod
    def get_role_by_name(db: Session, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()

    @staticmethod
    def get_all_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        return db.query(Role).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_roles(db: Session) -> List[Role]:
        return db.query(Role).filter(Role.is_active == True).all()

    @staticmethod
    def update_role(db: Session, role_id: int, data: RoleUpdate, updated_by: str = None) -> Optional[Role]:
        role = db.get(Role, role_id)
        if not role:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(role, key, value)
        
        role.updated_by = updated_by
        role.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        role = db.get(Role, role_id)
        if not role:
            return False
        
        # Soft delete - just mark as inactive
        role.is_active = False
        db.commit()
        return True

    # ============================================================================
    # PAGE PERMISSION METHODS
    # ============================================================================
    
    @staticmethod
    def create_page_permission(db: Session, data: PagePermissionCreate, created_by: str = None) -> PagePermissionResponse:
        page_permission = PagePermission(
            page_name=data.page_name,
            page_path=data.page_path,
            display_name=data.display_name,
            description=data.description,
            is_active=data.is_active,
            created_by=created_by
        )
        db.add(page_permission)
        db.commit()
        db.refresh(page_permission)
        return page_permission

    @staticmethod
    def get_page_permission_by_id(db: Session, page_id: int) -> Optional[PagePermission]:
        return db.query(PagePermission).filter(PagePermission.id == page_id).first()

    @staticmethod
    def get_page_permission_by_name(db: Session, page_name: str) -> Optional[PagePermission]:
        return db.query(PagePermission).filter(PagePermission.page_name == page_name).first()

    @staticmethod
    def get_all_page_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[PagePermission]:
        return db.query(PagePermission).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_page_permissions(db: Session) -> List[PagePermission]:
        return db.query(PagePermission).filter(PagePermission.is_active == True).all()

    @staticmethod
    def update_page_permission(db: Session, page_id: int, data: PagePermissionUpdate, updated_by: str = None) -> Optional[PagePermission]:
        page_permission = db.get(PagePermission, page_id)
        if not page_permission:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(page_permission, key, value)
        
        page_permission.updated_by = updated_by
        page_permission.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(page_permission)
        return page_permission

    @staticmethod
    def delete_page_permission(db: Session, page_id: int) -> bool:
        page_permission = db.get(PagePermission, page_id)
        if not page_permission:
            return False
        
        # Soft delete - just mark as inactive
        page_permission.is_active = False
        db.commit()
        return True

    # ============================================================================
    # ROLE PERMISSION METHODS
    # ============================================================================
    
    @staticmethod
    def create_role_permission(db: Session, data: RolePermissionCreate, created_by: str = None) -> RolePermissionResponse:
        role_permission = RolePermission(
            role_id=data.role_id,
            page_id=data.page_id,
            can_view=data.can_view,
            can_create=data.can_create,
            can_edit=data.can_edit,
            can_delete=data.can_delete,
            can_export=data.can_export,
            can_import=data.can_import,
            created_by=created_by
        )
        db.add(role_permission)
        db.commit()
        db.refresh(role_permission)
        return role_permission

    @staticmethod
    def get_role_permission_by_id(db: Session, permission_id: int) -> Optional[RolePermission]:
        return db.query(RolePermission).filter(RolePermission.id == permission_id).first()

    @staticmethod
    def get_role_permissions_by_role(db: Session, role_id: int) -> List[RolePermission]:
        return db.query(RolePermission).filter(RolePermission.role_id == role_id).all()

    @staticmethod
    def get_role_permissions_by_page(db: Session, page_id: int) -> List[RolePermission]:
        return db.query(RolePermission).filter(RolePermission.page_id == page_id).all()

    @staticmethod
    def update_role_permission(db: Session, permission_id: int, data: RolePermissionUpdate, updated_by: str = None) -> Optional[RolePermission]:
        role_permission = db.get(RolePermission, permission_id)
        if not role_permission:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(role_permission, key, value)
        
        role_permission.updated_by = updated_by
        role_permission.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(role_permission)
        return role_permission

    @staticmethod
    def delete_role_permission(db: Session, permission_id: int) -> bool:
        role_permission = db.get(RolePermission, permission_id)
        if not role_permission:
            return False
        
        db.delete(role_permission)
        db.commit()
        return True

    # ============================================================================
    # EMPLOYEE METHODS
    # ============================================================================
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def create_employee(db: Session, data: EmployeeCreate, created_by: str = None) -> Employee:
        hashed_password = EmployeeRoleCRUD.hash_password(data.password)
        
        employee = Employee(
            username=data.username,
            hashed_password=hashed_password,
            email=data.email,
            phone=data.phone,
            first_name=data.first_name,
            last_name=data.last_name,
            role_id=data.role_id,
            is_active=data.is_active,
            created_by=created_by
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return employee

    @staticmethod
    def get_employee_by_id(db: Session, employee_id: int) -> Optional[Employee]:
        return db.query(Employee).options(joinedload(Employee.role)).filter(Employee.id == employee_id).first()

    @staticmethod
    def get_employee_by_username(db: Session, username: str) -> Optional[Employee]:
        return db.query(Employee).options(joinedload(Employee.role)).filter(Employee.username == username).first()

    @staticmethod
    def get_employee_by_email(db: Session, email: str) -> Optional[Employee]:
        return db.query(Employee).options(joinedload(Employee.role)).filter(Employee.email == email).first()

    @staticmethod
    def get_employee_by_phone(db: Session, phone: str) -> Optional[Employee]:
        return db.query(Employee).options(joinedload(Employee.role)).filter(Employee.phone == phone).first()

    @staticmethod
    def get_all_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
        return db.query(Employee).options(joinedload(Employee.role)).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_employees(db: Session) -> List[Employee]:
        return db.query(Employee).options(joinedload(Employee.role)).filter(Employee.is_active == True).all()

    @staticmethod
    def update_employee(db: Session, employee_id: int, data: EmployeeUpdate, updated_by: str = None) -> Optional[Employee]:
        employee = db.get(Employee, employee_id)
        if not employee:
            return None

        update_data = data.dict(exclude_unset=True)
        
        # Handle password hashing if password is being updated
        if 'password' in update_data:
            update_data['hashed_password'] = EmployeeRoleCRUD.hash_password(update_data.pop('password'))
        
        for key, value in update_data.items():
            setattr(employee, key, value)
        
        employee.updated_by = updated_by
        employee.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(employee)
        return employee

    @staticmethod
    def delete_employee(db: Session, employee_id: int) -> bool:
        employee = db.get(Employee, employee_id)
        if not employee:
            return False
        
        # Soft delete - just mark as inactive
        employee.is_active = False
        db.commit()
        return True

    @staticmethod
    def authenticate_employee(db: Session, username: str, password: str) -> Optional[Employee]:
        """Authenticate an employee by username and password"""
        employee = db.query(Employee).options(joinedload(Employee.role)).filter(Employee.username == username).first()
        if not employee:
            return None
        
        if not EmployeeRoleCRUD.verify_password(password, employee.hashed_password):
            return None
        
        return employee

    # ============================================================================
    # PERMISSION METHODS
    # ============================================================================
    
    @staticmethod
    def get_user_permissions(db: Session, employee: Employee) -> List[Dict[str, Any]]:
        """Get all permissions for a specific user"""
        if not employee.role_id:
            return []
        
        # Get role permissions with page details
        permissions = db.query(RolePermission).join(PagePermission).filter(
            RolePermission.role_id == employee.role_id,
            PagePermission.is_active == True
        ).all()
        
        result = []
        for permission in permissions:
            result.append({
                'page_id': permission.page_id,
                'page_name': permission.page.page_name,
                'page_path': permission.page.page_path,
                'display_name': permission.page.display_name,
                'can_view': permission.can_view,
                'can_create': permission.can_create,
                'can_edit': permission.can_edit,
                'can_delete': permission.can_delete,
                'can_export': permission.can_export,
                'can_import': permission.can_import
            })
        
        return result

    @staticmethod
    def get_user_permissions_detailed(db: Session, employee: Employee) -> UserPermissions:
        """Get detailed user permissions including role information"""
        role = None
        if employee.role_id:
            role = EmployeeRoleCRUD.get_role_by_id(db, employee.role_id)
        
        permissions = EmployeeRoleCRUD.get_user_permissions(db, employee)
        
        pages = []
        for perm in permissions:
            pages.append(PageInfo(
                page_id=perm['page_id'],
                page_name=perm['page_name'],
                page_path=perm['page_path'],
                display_name=perm['display_name'],
                permissions={
                    'can_view': perm['can_view'],
                    'can_create': perm['can_create'],
                    'can_edit': perm['can_edit'],
                    'can_delete': perm['can_delete'],
                    'can_export': perm['can_export'],
                    'can_import': perm['can_import']
                }
            ))
        
        return UserPermissions(
            user_id=employee.id,
            username=employee.username,
            role=role,
            pages=pages
        )
