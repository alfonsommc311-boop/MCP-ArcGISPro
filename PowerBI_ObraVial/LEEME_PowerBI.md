# Obra Vial – Tablero interactivo en Power BI

Datos exportados desde MS Project (`Obra_Vial_Ejemplo.mpp`). Proyecto: **Construcción Carretera – Tramo Ejemplo (12 km)**, jul-2026 → dic-2027, costo ~$830 K, 29 actividades hoja + hitos, 22 tareas en ruta crítica.

## Archivos
- **Tareas.csv** — una fila por actividad (hojas + hitos). Columnas: ID, WBS, **Fase**, Tarea, Nivel, EsHito, EsCritica, Inicio, Fin, Duracion_dias, Avance_pct, HolguraTotal_dias, **Costo**, Recursos, Predecesoras.
- **Recursos.csv** — 13 recursos: Tipo, Tarifa, CostoTotal, NumTareas.

---

## 1) Importar (Power BI Desktop)
1. **Obtener datos → Texto/CSV** → `Tareas.csv`. En *Origen de archivo* elige **65001: Unicode (UTF-8)** (para los acentos). Cargar.
2. Repite con `Recursos.csv`.
3. En **Vista de tabla**, confirma tipos: `Inicio`/`Fin` = **Fecha**; `Costo`, `Duracion_dias`, `HolguraTotal_dias`, `Avance_pct` = **Número decimal/entero**; el resto **Texto**.

## 2) Tabla Calendario (DAX)
Crea una tabla nueva (*Modelado → Nueva tabla*):
```DAX
Calendario =
ADDCOLUMNS (
    CALENDAR ( DATE(2026,7,1), DATE(2027,12,31) ),
    "Año", YEAR([Date]),
    "Mes", FORMAT([Date], "MMM yyyy"),
    "MesOrden", YEAR([Date])*100 + MONTH([Date]),
    "Trimestre", "T" & FORMAT([Date],"Q yyyy")
)
```
Marca la columna `MesOrden` como *Ordenar por* de `Mes`, y **marca la tabla como tabla de fechas** (Date). Relación: `Calendario[Date]` → `Tareas[Inicio]` (activa).

## 3) Medidas DAX (Nueva medida)
```DAX
Costo Total = SUM ( Tareas[Costo] )
N Tareas = COUNTROWS ( FILTER ( Tareas, Tareas[EsHito] = "No" ) )
N Críticas = CALCULATE ( COUNTROWS(Tareas), Tareas[EsCritica] = "Sí" )
Avance Global % =
DIVIDE (
    SUMX ( Tareas, Tareas[Duracion_dias] * Tareas[Avance_pct] ),
    SUMX ( Tareas, Tareas[Duracion_dias] ) )
Inicio Proyecto = MIN ( Tareas[Inicio] )
Fin Proyecto = MAX ( Tareas[Fin] )
Duración Proyecto (días) = DATEDIFF ( [Inicio Proyecto], [Fin Proyecto], DAY )
% Costo Crítico =
DIVIDE (
    CALCULATE ( [Costo Total], Tareas[EsCritica]="Sí" ),
    [Costo Total] )
```

## 4) Visuales sugeridos (tablero interactivo)
Página 1 – **Resumen ejecutivo**
- 4 **Tarjetas**: `Costo Total`, `Avance Global %`, `Fin Proyecto`, `N Críticas`.
- **Segmentaciones (filtros)**: `Fase`, `EsCritica` (Sí/No), `Calendario[Mes]`.
- **Gráfico de barras apiladas**: Eje = `Fase`, Valor = `Costo Total` (costo por fase).
- **Gráfico de anillos**: `Costo Total` por `Tipo` de recurso (de Recursos) o por Fase.
- **Tabla**: Tareas con Inicio/Fin/Costo/EsCritica (se filtra al hacer clic en cualquier visual).

Página 2 – **Cronograma / Gantt**
- Instala el visual gratuito **"Gantt" de Microsoft** (AppSource / Obtener más visuales).
- Configúralo: *Task* = `Tarea`, *Start Date* = `Inicio`, *End Date* = `Fin`, *% Completion* = `Avance_pct`, *Legend* = `Fase` (o `EsCritica` para resaltar la ruta crítica en color), *Parent* = `Fase` para agrupar por fase.
- Añade la segmentación `EsCritica = Sí` para ver **solo la ruta crítica**.

Página 3 – **Recursos**
- Barras: `CostoTotal` por `Recurso` (tabla Recursos).
- Matriz: `Fase` × `Recurso` con `Costo`.

> Todo queda **interactivo**: al hacer clic en una fase, hito o recurso, el resto de visuales se filtra (cross-filtering nativo de Power BI).

---

## Notas
- **Materiales**: el costo de Material Granular/Mezcla/Concreto sale bajo (75/95/390) por una limitación del MCP de Project al cargar cantidades; la mano de obra y maquinaria sí reflejan el costo real. Se puede corregir editando `CostoTotal` en Recursos.csv si quieres un demo con cifras de material realistas.
- **Avance_pct** está en 0 (línea base sin avance). Si simulamos avance en Project, re-exporto y el `Avance Global %` y el Gantt se actualizan.
- **Fechas con hora**: se exportaron como fecha pura (YYYY-MM-DD).

## Alternativa automatizable (tras reiniciar Claude Code)
Con el **Power BI Modeling MCP** activo y un modelo abierto, puedo crear por mí mismo la tabla Calendario, las relaciones y todas las medidas DAX de arriba mediante lenguaje natural. Los **visuales** (Gantt, tarjetas, filtros) se colocan en el lienzo de Power BI — esa parte es manual o con el visual Gantt de AppSource.
