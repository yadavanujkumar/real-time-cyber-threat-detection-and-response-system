# src/core/model.py

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
    Text,
    UniqueConstraint,
    Index,
    create_engine,
    event,
)
from sqlalchemy.orm import relationship, declarative_base, validates, sessionmaker
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid

Base = declarative_base()

# Utility mixin for audit columns and soft deletes
class AuditMixin:
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete column

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()


# Utility mixin for UUID primary key
class UUIDMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)


# Core Models
class User(Base, UUIDMixin, AuditMixin):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    # Relationships
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")

    @validates("email")
    def validate_email(self, key, email):
        if "@" not in email:
            raise ValueError("Invalid email address")
        return email


class Threat(Base, UUIDMixin, AuditMixin):
    __tablename__ = "threats"

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Integer, nullable=False)  # 1 (Low) to 5 (Critical)
    metadata = Column(JSONB, nullable=True)  # Additional threat metadata

    # Relationships
    alerts = relationship("Alert", back_populates="threat", cascade="all, delete-orphan")

    @validates("severity")
    def validate_severity(self, key, severity):
        if not (1 <= severity <= 5):
            raise ValueError("Severity must be between 1 and 5")
        return severity


class Alert(Base, UUIDMixin, AuditMixin):
    __tablename__ = "alerts"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    threat_id = Column(UUID(as_uuid=True), ForeignKey("threats.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(50), nullable=False, default="new")  # e.g., new, in_progress, resolved
    details = Column(JSONB, nullable=True)  # Additional alert details

    # Relationships
    user = relationship("User", back_populates="alerts")
    threat = relationship("Threat", back_populates="alerts")

    @validates("status")
    def validate_status(self, key, status):
        allowed_statuses = {"new", "in_progress", "resolved"}
        if status not in allowed_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {allowed_statuses}")
        return status


# Indexing and Constraints
Index("ix_users_username", User.username, unique=True)
Index("ix_users_email", User.email, unique=True)
Index("ix_threats_name", Threat.name)
Index("ix_alerts_status", Alert.status)
Index("ix_alerts_timestamp", Alert.timestamp)

# Database Configuration
DATABASE_URL = "postgresql://user:password@localhost:5432/cyber_threat_db"

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20, pool_timeout=30)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Helper function to initialize the database
def init_db():
    Base.metadata.create_all(bind=engine)


# Event listener for soft delete filtering
@event.listens_for(SessionLocal, "do_orm_execute")
def add_soft_delete_filter(execute_state):
    if execute_state.is_select:
        for entity in execute_state.statement._entities:
            if hasattr(entity.entity_zero.class_, "deleted_at"):
                execute_state.statement = execute_state.statement.where(entity.entity_zero.class_.deleted_at.is_(None))


# Example Usage
if __name__ == "__main__":
    init_db()
    session = SessionLocal()

    # Create a new user
    new_user = User(username="cyber_admin", email="admin@example.com", hashed_password="hashedpassword123")
    session.add(new_user)
    session.commit()

    # Create a new threat
    new_threat = Threat(name="SQL Injection", description="Detected SQL injection attempt", severity=4)
    session.add(new_threat)
    session.commit()

    # Create an alert
    new_alert = Alert(user_id=new_user.id, threat_id=new_threat.id, status="new", details={"ip": "192.168.1.1"})
    session.add(new_alert)
    session.commit()

    print("Database initialized and sample data added.")