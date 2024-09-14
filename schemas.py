from datetime import datetime, date, time
from enum import Enum

from fastapi import HTTPException
from pydantic import BaseModel, model_validator


# Доступные типы посылок
class PackageType(str, Enum):
    letter = "Письмо"
    banderole = "Бандероль"
    oversized_cargo = "Габаритный груз"


# Доступные города доставки
class City(str, Enum):
    kzn = "Казань"
    nch = "Набережные Челны"
    nkm = "Нижнекамск"
    alm = "Альметьевск"
    zld = "Зеленодольск"


# Доступные статусы заказа
class DeliveryStatus(str, Enum):
    new = "new"
    in_progress = "in progress"
    handed_to_courier = "handed to courier"
    done = "done"
    cancelled = "cancelled"


class DeliveryRequestIn(BaseModel):
    delivery_city: City
    delivery_address: str
    delivery_date: date
    delivery_time: time
    customer_name: str
    comment: str | None = None
    package_type: PackageType

    @model_validator(mode='after')
    def check_package_type_and_city(self) -> 'DeliveryRequestIn':
        package_type = self.package_type
        delivery_city = self.delivery_city

        # Проверка, что Габаритный груз доставляется только в Казань
        if package_type == "Габаритный груз" and delivery_city != "Казань":
            raise HTTPException(status_code=400, detail="Габаритный груз доставляется только в Казани")

        return self


class DeliveryRequestOut(DeliveryRequestIn):
    internal_id: int
    load_date: datetime
    distance: float


class DeliveryStatusCreate(BaseModel):
    internal_id: int
    status_name: DeliveryStatus


class DeliveryStatusOut(DeliveryStatusCreate):
    load_date: datetime


class DeliveryStatusUpdate(BaseModel):
    new_status: DeliveryStatus
