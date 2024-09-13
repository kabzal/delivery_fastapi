from datetime import date, time, datetime

from sqlalchemy import Integer, Date, String, Time, ForeignKey, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from database import Base


class DeliveryRequests(Base):
    __tablename__ = "delivery_requests"

    internal_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    load_date: Mapped[datetime] = mapped_column(DateTime)
    delivery_city: Mapped[str] = mapped_column(String)
    delivery_address: Mapped[str] = mapped_column(String)
    distance: Mapped[float] = mapped_column(Float)
    delivery_date: Mapped[date] = mapped_column(Date)
    delivery_time: Mapped[time] = mapped_column(Time)
    customer_name: Mapped[str] = mapped_column(String)
    comment: Mapped[str] = mapped_column(String, nullable=True)
    package_type: Mapped[str] = mapped_column(String)


class DeliveryStatusCurrent(Base):
    __tablename__ = "delivery_status_current"

    internal_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("delivery_requests.internal_id", ondelete="CASCADE"),
        primary_key=True,
        index=True
    )
    status_name: Mapped[str] = mapped_column(String)
    load_date: Mapped[datetime] = mapped_column(DateTime)


class DeliveryStatusHistory(Base):
    __tablename__ = "delivery_status_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    internal_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("delivery_requests.internal_id", ondelete="CASCADE")
    )
    status_name: Mapped[str] = mapped_column(String)
    load_date: Mapped[datetime] = mapped_column(DateTime)


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    wh_city: Mapped[str] = mapped_column(String)
    wh_address: Mapped[str] = mapped_column(String)
    wh_lat: Mapped[float] = mapped_column(Float)
    wh_lon: Mapped[float] = mapped_column(Float)

    __table_args__ = (UniqueConstraint("wh_city", "wh_address", name="uq_city_address"),)

