from __future__ import annotations

from datetime import datetime
from typing import Optional

from flask_login import UserMixin
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.base import TimestampMixin


class Role(db.Model, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))

    users: Mapped[list[User]] = relationship("User", back_populates="role")


class User(db.Model, UserMixin, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

    role: Mapped[Role] = relationship("Role", back_populates="users")
    session_logs: Mapped[list[SessionLog]] = relationship("SessionLog", back_populates="user")
    admin_logs: Mapped[list[AdminLog]] = relationship("AdminLog", back_populates="user")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name: str) -> bool:
        return bool(self.role and self.role.name.lower() == role_name.lower())


class GalleryCategory(db.Model, TimestampMixin):
    __tablename__ = "gallery_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    images: Mapped[list[GalleryImage]] = relationship(
        "GalleryImage",
        back_populates="category",
        cascade="all, delete-orphan",
    )


class GalleryImage(db.Model, TimestampMixin):
    __tablename__ = "gallery_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("gallery_categories.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    webp_filename: Mapped[Optional[str]] = mapped_column(String(255))
    alt_text: Mapped[Optional[str]] = mapped_column(String(180))
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    category: Mapped[GalleryCategory] = relationship("GalleryCategory", back_populates="images")

    __table_args__ = (
        Index("idx_gallery_category_public", "category_id", "is_public"),
    )


class Services(db.Model, TimestampMixin):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price_label: Mapped[Optional[str]] = mapped_column(String(80))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ContactMessage(db.Model, TimestampMixin):
    __tablename__ = "contact_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(180), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))


class Settings(db.Model, TimestampMixin):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_name: Mapped[str] = mapped_column(String(120), default="Cruz Cofrade", nullable=False)
    site_description: Mapped[str] = mapped_column(
        String(255),
        default="Fotografía profesional de Semana Santa",
        nullable=False,
    )
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    instagram_url: Mapped[Optional[str]] = mapped_column(String(255))
    twitter_url: Mapped[Optional[str]] = mapped_column(String(255))


class SessionLog(db.Model):
    __tablename__ = "session_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    logged_in_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship("User", back_populates="session_logs")


class AdminLog(db.Model):
    __tablename__ = "admin_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(180), nullable=False)
    detail: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship("User", back_populates="admin_logs")
