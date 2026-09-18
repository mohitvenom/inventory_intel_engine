import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .session import Base

class SourceEnum(str, enum.Enum):
    amazon = 'amazon'
    ubuy = 'ubuy'

class AlertTypeEnum(str, enum.Enum):
    price_drop = 'price_drop'
    restock = 'restock'
    stockout = 'stockout'

class ChannelEnum(str, enum.Enum):
    slack = 'slack'
    email = 'email'

class RunStatusEnum(str, enum.Enum):
    running = 'running'
    success = 'success'
    failed = 'failed'

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(Enum(SourceEnum), nullable=False)
    external_id = Column(String, nullable=False, index=True)
    region = Column(String, nullable=True)
    name = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    price_drop_threshold_pct = Column(Float, default=5.0)
    notify_on_restock = Column(Boolean, default=True)
    notify_on_stockout = Column(Boolean, default=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    price_histories = relationship("PriceHistory", back_populates="product")
    stock_histories = relationship("StockHistory", back_populates="product")
    alerts_sent = relationship("AlertSent", back_populates="product")

class PriceHistory(Base):
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    price = Column(Numeric, nullable=False)
    currency = Column(String, nullable=False)
    checked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    
    product = relationship("Product", back_populates="price_histories")

class StockHistory(Base):
    __tablename__ = 'stock_history'
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    in_stock = Column(Boolean, nullable=False)
    checked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    
    product = relationship("Product", back_populates="stock_histories")

class AlertSent(Base):
    __tablename__ = 'alerts_sent'
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    alert_type = Column(Enum(AlertTypeEnum), nullable=False)
    message = Column(String, nullable=False)
    channel = Column(Enum(ChannelEnum), nullable=False)
    sent_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    product = relationship("Product", back_populates="alerts_sent")

class AgentRun(Base):
    __tablename__ = 'agent_runs'
    
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(RunStatusEnum), nullable=False)
    products_checked = Column(Integer, default=0)
    trace = Column(JSONB, nullable=True)
    error = Column(String, nullable=True)
