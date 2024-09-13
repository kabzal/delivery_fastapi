# Задание по SQL-запросам

Предисловие: задание выполнялось в PostgreSQL, что могло сказаться на подходах к решению.
Столбцы `LoadDate` перенес в БД в формате `timestamp`, а не `text`.
На всякий случай отмечу, что в предоставленных данных таблица `DeliveryStatusCurrent` 
не вполне соответствует таблице `DeliveryStatusHistory` (у одних и тех же заказов могут отличаться последние статусы);
также в таблице `DeliveryStatusHistory` бывает нарушена хронология статусов (например, `Handed to courier` уже после `Done`).

## Задание 1
Количество успешно завершенных заказов и их среднее время выполнения в разрезе городов.
Конструкция `AVG(EXTRACT(EPOCH FROM (dsc.LoadDate - dr.LoadDate)) / 3600)` считает среднее количество часов выполнения заказа.

Запрос:

```sql
SELECT
    dr.DeliveryCity AS city,
    COUNT(*) AS completed_orders,
    AVG(EXTRACT(EPOCH FROM (dsc.LoadDate - dr.LoadDate)) / 3600) AS avg_completion_time_hours
FROM DeliveryRequests dr
JOIN DeliveryStatusCurrent dsc ON dr.InternalId = dsc.InternalId
WHERE dsc.StatusName = 'Done'
GROUP BY dr.DeliveryCity
ORDER BY 2 DESC;
```

Результат:

| city | сompleted_orders | avg_completion_time_hours |
|---|---|---|
| Казань | 147 | 58.2676587301587302 |
| Набережные Челны | 129 | 58.0923018949181740 |
| Нижнекамск | 106 | 56.2775628930817610 |
| Альметьевск | 52 | 54.6927403846153846 |
| Зеленодольск | 28 | 59.9624107142857143 |

## Задание 2
Количество заявок в разрезе статусов, которые поступили за последние 3 недели с типом доставки «Письмо» и «Бандероль».
Исходил из предположения, что подразумевается за последние три недели с последнего заказа (в данном случае вышел период 19.08.2024-08.09.2024).

Запрос:

```sql
SELECT
    dsc.StatusName AS status,
    Count(dr.InternalId) AS requests_count
FROM DeliveryRequests dr
JOIN DeliveryStatusCurrent dsc ON dr.InternalId = dsc.InternalId
WHERE
    DATE_TRUNC('day', dr.loaddate) > (SELECT DATE_TRUNC('day', MAX(dr.loaddate) - INTERVAL '3 weeks') FROM DeliveryRequests dr)
    AND dr.packagetype in ('Письмо', 'Бандероль')
GROUP BY dsc.StatusName
ORDER BY 2 DESC;
```

Результат:

| status | requests_count |
|---|---|
| Done | 12 |
| Handed to courier | 9 |
| New | 8 |
| Cancelled | 4 |
| In Progress | 2 |

## Задание 3
Среднее время нахождение заявки на каждом этапе в городе Казань в разрезе типа посылки для завершенных заявок.
Здесь также конструкция `AVG(EXTRACT(epoch FROM st.duration_days) / 3600)` считает среднее количество часов нахождения на каждом этапе.
Фактически считается время на этапах: `New`; `In Progress`; `Handed to courier`.
`Done` отсутствует, так как это момент завершения, а не этап. Статус `Cancelled` не соответствует условиям задачи.

Запрос:
```sql
WITH status_times AS (
SELECT
    dh.InternalId,
    dh.StatusName as status,
    dh.LoadDate,
    LEAD(dh.LoadDate) OVER (PARTITION BY dh.InternalId ORDER BY dh.LoadDate) - dh.LoadDate AS duration_days
FROM DeliveryStatusHistory dh
)

SELECT
    dr.PackageType AS package_type,
    st.status AS status,
    AVG(EXTRACT(epoch FROM st.duration_days) / 3600) AS avg_hours
FROM
    status_times st
JOIN
    DeliveryStatusCurrent ds ON ds.InternalId = st.InternalId
JOIN
    DeliveryRequests dr ON dr.InternalId = ds.InternalId
WHERE
    dr.DeliveryCity = 'Казань'
    AND ds.StatusName = 'Done' /* Берем только заказы с текущим статусом Done */
    AND st.status <> 'Done'  /* Убираем статус Done из результата, так как он не является этапом и его время = NULL */
GROUP BY
    dr.PackageType,
    st.status
ORDER BY
    dr.PackageType,
    st.status DESC;
```

Результат:

| package_type      | status              | avg_hours                       |
|-------------------|--------------------|---------------------------------|
| Бандероль         | New                | 16.10400118203309691868         |
| Бандероль         | In Progress         | 31.72259578544061302989         |
| Бандероль         | Handed to courier  | 28.20124113475177305697         |
| Габаритный груз   | New                | 16.22491228070175437544         |
| Габаритный груз   | In Progress         | 26.62472222222222222680         |
| Габаритный груз   | Handed to courier  | 29.86788011695906432485         |
| Письмо            | New                | 13.97840501792114695753         |
| Письмо            | In Progress         | 23.71430555555555555769         |
| Письмо            | Handed to courier  | 30.2526568100358423             |




