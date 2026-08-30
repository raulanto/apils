from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from apils.infrastructure.database import Base
import uuid

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", String(36), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles", lazy="selectin")
    users = relationship("User", secondary=user_roles, back_populates="roles")


class Action(Base):
    __tablename__ = "actions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    permissions = relationship("Permission", back_populates="action")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    permissions = relationship("Permission", back_populates="resource")


class PermissionGroup(Base):
    __tablename__ = "permission_groups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    permissions = relationship("Permission", back_populates="group")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action_id = Column(String(36), ForeignKey("actions.id", ondelete="CASCADE"), nullable=False)
    resource_id = Column(String(36), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(String(36), ForeignKey("permission_groups.id", ondelete="SET NULL"), nullable=True)
    description = Column(String(255), nullable=True)

    action = relationship("Action", back_populates="permissions", lazy="joined")
    resource = relationship("Resource", back_populates="permissions", lazy="joined")
    group = relationship("PermissionGroup", back_populates="permissions", lazy="joined")

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    @property
    def name(self):
        if self.resource and self.action:
            return f"{self.resource.name}:{self.action.name}"
        return None
