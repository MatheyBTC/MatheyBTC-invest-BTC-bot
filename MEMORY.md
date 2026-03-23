# MEMORY — MatheyBTC-invest-BTC
_Última actualización: 2026-03-23_

## Estado Actual
App funcional en GitHub Pages. Plan A y Plan B completamente actualizados.
Semáforo expandido a 8 ventanas de tiempo. Plan C y D no tocados en esta sesión.

## Última Sesión
**Fecha:** 2026-03-23

### Plan A
- Removido `text-transform:uppercase` de labels y th en CSS
- `USD` → `U$S` en toda la UI
- Backtesting: `Años` → `Ciclos`, `Precio Promedio` → `Precio Medio`, `Valor Actual` → `Valor Actual (Cartera)`
- `renderChartA`: removido `borderDash` del dataset Total Invertido
- `renderFreqComparison`: reescrito — mismo capital total para todas las frecuencias (base = diaria), filas color verde/amarillo/naranja/rojo
- `renderSemaphore`: expandido a 8 ventanas, thresholds 30/25/20/15/10
- `renderMA90`: labels en Title Case, removido `borderDash` de línea MA90
- X-axis 2 filas: año arriba, Mes/dd abajo con `MESES_CORTOS` array

### Plan B
- Rediseñado: trigger MA90 → vende X% del stack → compra BTC lump sum al toque
- Cooldown 30 días entre triggers, máximo 11 eventos/año
- Botones rápidos sell%: 5% verde, 8% amarillo, 10% rojo + campo manual
- Tabla "Historial De Compras Puntuales" con filas en fondo naranja
- Columna BTC Recomprado en tabla
- Comparativa: Plan A caja azul, Plan B caja naranja; línea Plan A sólida
- Fix bugs: precio promedio ya no da 0, total invertido ya no da 0

### Semáforo
- Título: "Precio Actual vs Promedio de Compra por Ventanas de Tiempo"
- 8 ventanas: APY60, APY90, APY180, 12 Meses, 2 Ciclos(x24), 3(x36), 4(x48), 5(x60)
- Celda: "Valor = U$S X", flecha 26px, sin text-transform:uppercase
- Leyenda: solo % (🟩30% 🟨25% 🟧20% 🟥15% 🟦10%)

## Pendiente / Próximos Pasos
1. Revisar Plan C (Colateral) — no fue tocado, puede tener issues de formato/UX
2. Revisar Plan D (señales T3-CCI) — no fue tocado
3. Implementar MatheyBTC-DCA-plan (proyecto separado, spec aprobada, plan listo)
4. Verificar que `btc_prices.json` esté actualizado con precios recientes

## Decisiones Técnicas Clave
- U$S siempre (no USD) en la UI
- Title Case en todos los labels del HTML
- `renderFreqComparison`: mismo capital total para todas las frecuencias (no mismo monto por compra)
- Plan B trigger: sell + rebuy inmediato al MISMO precio (lump sum, no sub-DCA ni DCA distribuido)
- Semáforo usa `currentPrice` (último precio del dataset) vs precio promedio de compra del período
- `getMA90AtDate()` devuelve 0 si hay menos de 89 días de datos previos

## Contexto Importante
- Repo: `MatheyBTC/MatheyBTC-invest-BTC` — deployed en GitHub Pages
- Precios se cargan desde Google Sheets CSV (URL en index.html)
- `btc_prices.json` se copia a `MatheyBTC-DCA-plan` cuando se implemente
- Notas de cambios en `Notas/PlanA.txt` y `Notas/Plan B.txt`
