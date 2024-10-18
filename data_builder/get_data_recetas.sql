-- Definición de variables iniciales
DECLARE @sitio1 VARCHAR(10) = (SELECT TOP(1) sitio FROM costos_articulos ORDER BY 1 DESC);
DECLARE @sitio2 VARCHAR(10) = (SELECT TOP(1) sitio FROM costos_articulos WHERE sitio <> @sitio1 ORDER BY 1 DESC);

-- Declaración de variables para controlar los parámetros de búsqueda
DECLARE @likeDescripcionPAPA VARCHAR(50) = '%PAPA%';
DECLARE @likeDescripcionPAPAFRITA VARCHAR(50) = '%PAPA FRITA%';
DECLARE @unidadReceta VARCHAR(12) = 'UNIDAD';
DECLARE @unidadRecetaFiltro VARCHAR(12) = 'KG';
DECLARE @codCadena INT = 10;

-- Subconsulta para obtener Cantidad y Unidad_Receta filtrando por PAPA
WITH CantidadUnidad AS (
    SELECT 
        SRT.Cantidad, 
        Unidad_Receta = CONVERT(CHAR(12), CA.Unidad_Receta),
        SR.Cod_Subrecet
    FROM 
        SubRecet SR
        JOIN SubRecetaTrans SRT ON SR.Cod_Subrecet = SRT.Cod_Subrecet
        JOIN Articulos A ON SRT.Cod_Articulo = A.Cod_Articulo
        JOIN Costos_Articulos CA ON CA.cod_articulo = A.cod_articulo
    WHERE 
        CA.sitio = @sitio1 
        AND SRT.Cod_Articulo_Sub IS NULL 
        AND SRT.estado = 1 
        AND CA.cod_cadena = @codCadena
        AND A.Nombre LIKE @likeDescripcionPAPA
    UNION ALL
    SELECT 
        SRT.Cantidad, 
        Unidad_Receta = CONVERT(CHAR(12), CA.Unidad_Receta),
        SR.Cod_Subrecet
    FROM 
        SubRecet SR
        JOIN SubRecetaTrans SRT ON SR.Cod_Subrecet = SRT.Cod_Subrecet
        JOIN Articulos A ON SRT.Cod_Articulo = A.Cod_Articulo
        JOIN Costos_Articulos CA ON CA.cod_articulo = A.cod_articulo
    WHERE 
        CA.sitio = @sitio2 
        AND SRT.Cod_Articulo_Sub IS NULL 
        AND CA.Cod_Articulo NOT IN (SELECT Cod_Articulo FROM Costos_Articulos WHERE Sitio = @sitio1 AND cod_cadena = @codCadena)
        AND SRT.estado = 1 
        AND CA.cod_cadena = @codCadena
        AND A.Nombre LIKE @likeDescripcionPAPA
    UNION ALL
    SELECT 
        SRT.Cantidad, 
        Unidad_Receta = CONVERT(CHAR(12), SR.Unidad_Receta) COLLATE MODERN_SPANISH_CI_AI,
        SR.Cod_Subrecet
    FROM 
        SubRecetaTrans SRT
        JOIN SubRecet SR ON SRT.Cod_Articulo_Sub = SR.Cod_Subrecet
    WHERE 
        SRT.Cod_Articulo IS NULL 
        AND SRT.estado = 1 
        AND SR.Descripcion LIKE @likeDescripcionPAPA
)

-- Consulta principal unida con la subconsulta, filtrando por Unidad_Receta = 'GR'
SELECT DISTINCT 
    Plus.Cod_Plu, 
    Plus.Descripcion AS Descripcion_Plu, 
    SubRecet.Descripcion AS Descripcion_SubRecet,
    CU.Cantidad,
    CU.Unidad_Receta
FROM 
    Plus
INNER JOIN 
    Recetas ON Recetas.Cod_Plu = Plus.Cod_Plu
INNER JOIN 
    SubRecet ON SubRecet.Cod_Subrecet = Recetas.Cod_Subrecet
LEFT JOIN 
    CantidadUnidad CU ON CU.Cod_Subrecet = SubRecet.Cod_Subrecet
WHERE 
    SubRecet.Descripcion LIKE @likeDescripcionPAPAFRITA
    AND SubRecet.Unidad_Receta = @unidadReceta
    AND Plus.Cod_Cadena = @codCadena
	AND Plus.Estado = 1
    AND CU.Unidad_Receta = @unidadRecetaFiltro;  -- Filtrar solo registros donde Unidad_Receta sea 'GR'
