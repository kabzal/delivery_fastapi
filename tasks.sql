
/* Предисловие: задание выполнялось в PostgreSQL, что могло сказаться на подходах к решению.
Столбцы LoadDate перенес в БД в формате timestamp, а не text.

Задание 1. Количество успешно завершенных заказов и их среднее время выполнения в разрезе городов.
Конструкция AVG(EXTRACT(EPOCH FROM (dsc.LoadDate - dr.LoadDate)) / 3600) считает среднее количество часов выполнения заказа. */
SELECT
	dr.DeliveryCity AS city,
	COUNT(*) AS completed_orders,
	AVG(EXTRACT(EPOCH FROM (dsc.LoadDate - dr.LoadDate)) / 3600) AS avg_completion_time_hours
FROM DeliveryRequests dr
JOIN DeliveryStatusCurrent dsc ON dr.InternalId = dsc.InternalId
WHERE dsc.StatusName = 'Done'
GROUP BY dr.DeliveryCity
ORDER BY 2 DESC;

/* Задание 2. Количество заявок в разрезе статусов, которые поступили за последние 3 недели с типом доставки «Письмо» и «Бандероль».
Исходил из предположения, что подразумевается за последние три недели с последнего заказа (08.09.2024). */
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


/* Задание 3. Среднее время нахождение заявки на каждом этапе в городе Казань в разрезе типа посылки для завершенных заявок.
Здесь также конструкция AVG(EXTRACT(epoch FROM st.duration_days) / 3600) считает среднее количество часов нахождения на каждом этапе.
Фактически считается время на этапах: 'New'; 'In Progress'; 'Handed to courier'.
'Done' отсутствует, так как это момент завершения, а не этап. Статус 'Cancelled' не соответствует условиям задачи. */
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
