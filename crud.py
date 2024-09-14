from datetime import datetime, timedelta

from fastapi import HTTPException
from geopy import distance
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from dadata_tools import check_address


# Получение заявки
async def get_delivery_request(db: AsyncSession, internal_id: int):
    result = await db.execute(
        select(models.DeliveryRequests).where(models.DeliveryRequests.internal_id == internal_id)
    )
    delivery_request = result.scalars().first()
    if delivery_request:
        return delivery_request
    else:
        raise HTTPException(status_code=404, detail=f'Заявка №{internal_id} не найдена.')


# Создание заявки
async def create_request(db: AsyncSession, request: schemas.DeliveryRequestIn):

    now_moment_moscow = datetime.utcnow() + timedelta(hours=3, minutes=0)  # Текущая дата по МСК
    # Выгружаем скорректированные данные об адресе
    address_data = await check_address(city=request.delivery_city.value, address=request.delivery_address)
    # Получаем расстояние до склада
    warehouse_distance = await get_warehouse_distance(db=db, city=request.delivery_city, address_data=address_data)

    # Формируем новый заказ
    new_request = models.DeliveryRequests(
        load_date=now_moment_moscow,  # Время создания заказа - текущее по МСК
        delivery_city=request.delivery_city,
        delivery_address=address_data['result'],  # Скорректированный адрес
        distance=warehouse_distance,  # Рассчитанное расстояние до склада
        delivery_date=request.delivery_date,
        delivery_time=request.delivery_time,
        customer_name=request.customer_name,
        comment=request.comment,
        package_type=request.package_type
    )

    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)

    return new_request


# Обновление заявки
async def update_request(db: AsyncSession, internal_id: int, request_update: schemas.DeliveryRequestIn):
    # Проверяем, существует ли заказ
    existing_request = await get_delivery_request(db=db, internal_id=internal_id)

    # Получаем откорректированный адрес и расстояние до склада
    address_data = await check_address(
        city=request_update.delivery_city.value,
        address=request_update.delivery_address
    )
    warehouse_distance = await get_warehouse_distance(
        db=db,
        city=request_update.delivery_city,
        address_data=address_data
    )

    # Обновляем поля заказа
    existing_request.delivery_city = request_update.delivery_city
    existing_request.delivery_address = address_data['result']  # Скорректированный адрес
    existing_request.delivery_date = request_update.delivery_date
    existing_request.delivery_time = request_update.delivery_time
    existing_request.customer_name = request_update.customer_name
    existing_request.comment = request_update.comment
    existing_request.package_type = request_update.package_type
    existing_request.distance = warehouse_distance   # Рассчитанное расстояние до склада

    # Обновляем запись в БД
    db.add(existing_request)
    await db.commit()

    return {"message": f"Заявка №{internal_id} успешно обновлена"}


# Получение статуса по заявке
async def get_status(db: AsyncSession, internal_id: int):
    result = await db.execute(
        select(models.DeliveryStatusCurrent).where(models.DeliveryStatusCurrent.internal_id == internal_id)
    )
    status = result.scalars().first()
    if status:
        return status
    else:
        raise HTTPException(status_code=404, detail='Статус такой заявки не найден.')


# Создание и изменение статуса заявки
async def create_status(db: AsyncSession, status_name: schemas.DeliveryStatus, internal_id: int):

    now_moment_moscow = datetime.utcnow() + timedelta(hours=3)  # Текущая дата по МСК

    # Создаем новую запись о статусе
    new_current_status = models.DeliveryStatusCurrent(
        internal_id=internal_id,
        status_name=status_name,
        load_date=now_moment_moscow
    )
    db.add(new_current_status)

    # Теперь дополняем историю статусов
    new_history_record = models.DeliveryStatusHistory(
        internal_id=internal_id,
        status_name=status_name,
        load_date=now_moment_moscow
    )
    db.add(new_history_record)

    await db.commit()

    return {"message": f"Установлен статус Заявки №{internal_id}: {status_name.value}"}


# Функция для обновления статуса
async def update_status(db: AsyncSession, status_name: schemas.DeliveryStatus, internal_id: int):

    now_moment_moscow = datetime.utcnow() + timedelta(hours=3)  # Текущая дата по МСК

    # Получаем запись с internal_id и меняем имя статуса и дату установки
    current_status = await get_status(db=db, internal_id=internal_id)
    current_status.status_name = status_name
    current_status.load_date = now_moment_moscow   # Время установки статуса - текущее по МСК

    # Теперь дополняем историю статусов
    new_history_record = models.DeliveryStatusHistory(
        internal_id=internal_id,
        status_name=status_name,
        load_date=now_moment_moscow   # Время установки статуса - текущее по МСК
    )
    db.add(new_history_record)

    await db.commit()

    return {"message": f"Новый статус Заявки №{internal_id}: {status_name.value}"}


# Функция для получения склада из БД и рассчета расстояния до адреса доставки
async def get_warehouse_distance(db: AsyncSession, city: schemas.City, address_data: dict):
    result = await db.execute(
        select(models.Warehouse).where(models.Warehouse.wh_city == city)
    )
    warehouse = result.scalars().first()
    if warehouse:
        warehouse_distance = distance.distance(
            (float(address_data['geo_lat']), float(address_data['geo_lon'])),
            (warehouse.wh_lat, warehouse.wh_lon)
        ).km
        return warehouse_distance
    else:
        raise HTTPException(status_code=404, detail='Нет склада в указанном городе')
