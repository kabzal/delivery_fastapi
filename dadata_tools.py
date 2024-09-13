from dadata import DadataAsync
from fastapi import HTTPException
from httpx import ConnectTimeout

import config

token = config.DADATA_TOKEN
secret = config.DADATA_SECRET


# Функция для поиска адреса в Dadata
async def check_address(city: str, address: str) -> dict | HTTPException:
    try:
        async with DadataAsync(token, secret) as dadata:
            result = await dadata.clean("address", f"Татарстан, {city}, {address}")
    except ConnectTimeout:
        raise HTTPException(status_code=504, detail="Сервис не отвечает. Попробуйте позже.")

    if result and result['result'] not in ("г Казань", f"Респ Татарстан, г {city}"):
        return result
    else:
        raise HTTPException(status_code=400, detail="Произошла ошибка при попытке найти адрес.")
