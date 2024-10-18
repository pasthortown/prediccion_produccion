DECLARE @fecha_minima DATETIME, @fecha_maxima DATETIME, @intervalo_minutos INT;
SET @fecha_minima = ?;
SET @fecha_maxima = ?;
SET @intervalo_minutos = ?;

WITH IntervalSeries AS (
    SELECT 
        DATEADD(MINUTE, 0, @fecha_minima) AS fecha_inicio,
        DATEADD(MINUTE, @intervalo_minutos, @fecha_minima) AS fecha_fin
    UNION ALL
    SELECT 
        DATEADD(MINUTE, @intervalo_minutos, fecha_inicio),
        DATEADD(MINUTE, @intervalo_minutos, fecha_fin)
    FROM 
        IntervalSeries
    WHERE 
        DATEADD(MINUTE, @intervalo_minutos, fecha_inicio) < @fecha_maxima
)
SELECT 
    subquery.plu_num_plu, 
    COUNT(subquery.plu_num_plu) AS 'Cuenta',
    IntervalSeries.fecha_inicio,
    IntervalSeries.fecha_fin
FROM 
    IntervalSeries
CROSS APPLY (
    SELECT 
        Plus.plu_num_plu
    FROM 
        Detalle_Factura 
    INNER JOIN 
        Plus ON Detalle_Factura.plu_id = Plus.plu_id
    INNER JOIN 
        Cabecera_Factura ON Cabecera_Factura.cfac_id = Detalle_Factura.cfac_id
    WHERE 
        Cabecera_Factura.cfac_fechacreacion >= IntervalSeries.fecha_inicio
        AND Cabecera_Factura.cfac_fechacreacion < IntervalSeries.fecha_fin
) AS subquery
GROUP BY 
    subquery.plu_num_plu, 
    IntervalSeries.fecha_inicio, 
    IntervalSeries.fecha_fin
ORDER BY 
    IntervalSeries.fecha_inicio
OPTION (MAXRECURSION 1000);
