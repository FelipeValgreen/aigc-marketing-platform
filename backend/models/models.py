from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.database import Base

class Agency(Base):
    __tablename__ = "agencies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    clients = relationship("Client", back_populates="agency", cascade="all, delete-orphan")

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=True) # Podría ser Null temporalmente al onboardear sin agencia
    company_name = Column(String, index=True, nullable=False)
    website_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    agency = relationship("Agency", back_populates="clients")
    brand_guidelines = relationship("BrandGuidelines", back_populates="client", uselist=False, cascade="all, delete-orphan")
    social_auths = relationship("SocialAuth", back_populates="client", cascade="all, delete-orphan")

class BrandGuidelines(Base):
    __tablename__ = "brand_guidelines"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), unique=True, nullable=False)
    primary_color_hex = Column(String, nullable=True)
    secondary_color_hex = Column(String, nullable=True)
    typography_name = Column(String, nullable=True)
    tone_of_voice = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    value_proposition = Column(Text, nullable=True)

    client = relationship("Client", back_populates="brand_guidelines")

class SocialAuth(Base):
    __tablename__ = "social_auths"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    platform_name = Column(String, index=True, nullable=False) # ej. 'meta', 'tiktok'
    access_token = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    client = relationship("Client", back_populates="social_auths")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    product_name = Column(String, nullable=True)
    product_desc = Column(Text, nullable=True)
    video_angle = Column(String, nullable=True)
    custom_media_path = Column(String, nullable=True)
    music_style = Column(String, nullable=True)
    status = Column(String, default="ESPERANDO_GUION")
    script_json = Column(Text, nullable=True)
    avatar_id = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", backref="projects")
