from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud import create_request, create_status, update_status, get_status, get_delivery_request, update_request
from database import get_db
from schemas import DeliveryRequestIn, DeliveryStatus, DeliveryStatusOut, DeliveryRequestOut

app = FastAPI(
    title="Управление заказами"
)


# Получение данных о заявке по internal_id
@app.get("/request/{internal_id}/", response_model=DeliveryRequestOut)
async def get_delivery_request_endpoint(
        internal_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Введите internal_id заявки, сведения о которой хотите посмотреть.
    """
    delivery_request = await get_delivery_request(db=db, internal_id=internal_id)
    return delivery_request


# Создание заказа
@app.post("/request/")
async def create_delivery_request_endpoint(
        request: DeliveryRequestIn,
        db: AsyncSession = Depends(get_db)
):
    """
        Отправьте Body с параметрами заявки, который хотите создать.

        Ограничения:
            delivery_city: Доступны только Казань, Набережные Челны, Нижнекамск, Альметьевск, Зеленодольск.
            package_type: Доступны Письмо, Бандероль, Габаритный груз. Габаритный груз - только в Казани.
            delivery_date: дату доставки указывать в формате ГГГГ-ММ-ДД.

        Комментарий (comment) указывать необязательно. Если хотите оставить его пустым, удалите его из Body.

        Функция возвращает internal_id вновь созданной заявки.
    """

    new_request = await create_request(db=db, request=request)  # сохраняем заказ в БД

    # Сразу создаем записи в таблицах со статусами
    status_change = await create_status(
        db=db,
        status_name=DeliveryStatus.new,
        internal_id=new_request.internal_id
    )

    return {"new_request_internal_id": new_request.internal_id}  # Возвращаем internal_id


# Обновление заявки
@app.put("/request/{internal_id}/")
async def update_delivery_request_endpoint(
        internal_id: int,
        request_update: DeliveryRequestIn,  # Данные для обновления
        db: AsyncSession = Depends(get_db)
):
    """
        Укажите internal_id заявки и отправьте Body с параметрами заявки, которую хотите обновить.
    """

    message = await update_request(db=db, internal_id=internal_id, request_update=request_update)
    return message


# Просмотр текущего статуса заказа
@app.get("/request/{internal_id}/status", response_model=DeliveryStatusOut)
async def get_delivery_status(
        internal_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
        Укажите internal_id заявки, текущий статус которой хотите получить.
    """

    current_status = await get_status(db=db, internal_id=internal_id)

    return current_status


# Изменение текущего статуса заказа
@app.put("/request/{internal_id}/status")
async def update_delivery_status(
        internal_id: int,
        new_status: DeliveryStatus,
        db: AsyncSession = Depends(get_db)
):
    """
        Укажите internal_id заявки, текущий статус которой хотите изменить, и укажите новый статус.
    """

    message = await update_status(db=db, status_name=new_status, internal_id=internal_id)

    return message
