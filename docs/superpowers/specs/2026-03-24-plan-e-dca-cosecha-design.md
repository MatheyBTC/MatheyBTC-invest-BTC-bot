# Plan E) DCA Cosecha — Diseño v1.1

**Proyecto:** MatheyBTC-invest-BTC (`index.html`)
**Fecha:** 2026-03-24
**Estado:** APROBADA

---

## Descripción

Nueva tab de simulación que implementa una estrategia DCA con "cosecha de ganancias": vende un % del stack cuando el precio supera el costo promedio propio en X%, y recompra lump sum cuando el precio baja Y% desde el precio de venta. Si la recompra no ocurre en 3 meses, los USD se re-invierten en el DCA base.

Propósito: herramienta exploratoria — el usuario puede simular el impacto de tomar ganancias parciales y ver cuándo/si logra recomprar más barato.

---

## Ubicación en la App

- Nueva tab al final: `Plan E) DCA Cosecha`, después de Plan D) Trading
- Acceso desde barra de tabs: `Plan A) | Plan B) | Plan C) | Plan D) | Plan E) | Dashboard`
- Tab ID: `tab-planE`

---

## Parámetros de Entrada

| Campo | Tipo | Default | Descripción |
|---|---|---|---|
| Monto por Compra (U$S) | number | 100 | Capital base del DCA |
| Frecuencia | select | Mensual (30) | Diaria / Semanal / Bisemanal / Mensual |
| Fecha Inicio | date | 2020-01-01 | Inicio de la simulación |
| Fecha Fin | date | hoy | Fin de la simulación |
| Umbral de Venta % | number | 50 | Vender cuando precio > costo_propio × (1 + X%) |
| % del Stack a Vender | number | 10 | Porcentaje del BTC acumulado a vender |
| Umbral de Recompra % | number | 20 | Recomprar cuando precio ≤ precio_venta × (1 - Y%) |

### Botones de acceso rápido

**Umbral de Venta** (color = agresividad de la señal):
- `25%` rojo · `50%` naranja · `75%` amarillo · `100%` verde · [manual]

**% del Stack a Vender:**
- `5%` verde · `10%` amarillo · `15%` rojo · [manual]

**Umbral de Recompra:**
- `5%` rojo · `10%` naranja · `15%` amarillo · `25%` verde · [manual]

---

## Lógica de Cálculo

### Estado interno del algoritmo

```
btcStack        // BTC actualmente en cartera (decrece con ventas, crece con compras)
btcBought       // BTC total comprado históricamente (nunca decrece — base para costPromedio)
totalInvested   // USD total invertido en compras (nunca decrece)
costPromedio    // = totalInvested / btcBought (refleja costo histórico, no se ajusta por ventas)
usdEspera       // USD retenido esperando recompra (0 si no hay ciclo abierto)
precioVenta     // Precio al que se vendió en el ciclo abierto
mesesEspera     // Contador de meses sin recompra (0..3)
lastSaleDate    // Fecha de última venta (para cooldown)
harvestCount    // Contador de cosechas completadas (✅ + 🔄) — para sub-label stat box
fallbackQueue   // Array de cuotas fallback pendientes: [{ date, amount }]
cycles          // Array de ciclos registrados para tabla 🌾
checkDates      // Array de fechas de chequeo mensual (startDate + 30, +60, ...) — fijo, no se resetea por ventas
equity          // Array de { date, btc, value } — un entry por día, para el gráfico comparativo
```

**Nota sobre `costPromedio`:** `btcBought` y `totalInvested` **no se decrementan** al vender. El costo promedio refleja el precio promedio histórico de todas las compras, independientemente de ventas. Esto evita que el trigger de venta se re-active inmediatamente después de una venta parcial, ya que el costo promedio permanece estable.

### Algoritmo (loop diario)

```
checkDates = [startDate + 30d, startDate + 60d, startDate + 90d, ...]

para cada día d desde startDate hasta endDate:
  precio = getPriceAt(d)

  // 1. Ejecutar cuotas fallback pendientes
  para cada cuota en fallbackQueue donde cuota.date <= d:
    btc = cuota.amount / precio
    btcStack += btc
    btcBought += btc
    totalInvested += cuota.amount
    recalcular costPromedio
    remover cuota de fallbackQueue

  // 2. Ejecutar compra DCA base pendiente
  si d >= nextBuyDate:
    btc = amount / precio
    btcStack += btc
    btcBought += btc
    totalInvested += amount
    recalcular costPromedio = totalInvested / btcBought
    nextBuyDate = d + freqDays

  // 3. Chequeo mensual (solo en checkDates — reloj fijo desde startDate, no se resetea)
  si d está en checkDates:

    // 3a. ¿Hay USD esperando recompra?
    si usdEspera > 0:
      si precio <= precioVenta × (1 - umbralRecompra/100):
        → RECOMPRA lump sum:
          btc = usdEspera / precio
          btcStack += btc; btcBought += btc; totalInvested += usdEspera
          recalcular costPromedio
          marcar ciclo actual como ✅ Recomprado, detalle = (d, precio)
          harvestCount += 1
          usdEspera = 0; precioVenta = null; mesesEspera = 0
      sino:
        mesesEspera += 1
        si mesesEspera >= 3 Y daysBetween(lastSaleDate, d) >= 90:
          → FALLBACK: agregar 3 cuotas a fallbackQueue:
              cuota1 = { date: d + 30d, amount: usdEspera/3 }
              cuota2 = { date: d + 60d, amount: usdEspera/3 }
              cuota3 = { date: d + 90d, amount: usdEspera/3 }
            marcar ciclo como 🔄 Re-invierte, detalle = mes del fallback
            harvestCount += 1
            usdEspera = 0; precioVenta = null; mesesEspera = 0

    // 3b. ¿Condición de venta? (solo si no hay USD esperando)
    sino si btcStack > 0:
      cooldownOk = (lastSaleDate == null) OR (daysBetween(lastSaleDate, d) >= 30)
      si cooldownOk Y precio > costPromedio × (1 + umbralVenta/100):
        btcToSell = btcStack × pctVenta/100
        usdObtenido = btcToSell × precio
        pctSobreCosto = (precio / costPromedio - 1) × 100
        btcStack -= btcToSell
        // btcBought y totalInvested NO se modifican
        usdEspera = usdObtenido
        precioVenta = precio
        lastSaleDate = d
        mesesEspera = 0
        cycles.push({ id, fecha: d, precioVenta, btcVendido: btcToSell,
                      usdObtenido, pctSobreCosto, estado: '⏳', detalle: '' })

  equity.push({ date: d, btc: btcStack, value: btcStack × precio })

// Al terminar el loop:
currentValue = btcStack × getPriceAt(endDate)  // último precio disponible en el rango
```

### Reglas clave
- **Un ciclo a la vez:** no se puede vender si `usdEspera > 0`
- **Cooldown 30 días** entre ventas (`lastSaleDate`)
- **Reloj mensual fijo:** `checkDates` calculados desde `startDate`, no se resetean por ventas
- **Fallback:** 3 cuotas sintéticas inyectadas en los próximos 3 meses (día +30, +60, +90 desde el chequeo del mes 3). Si una cuota cae el mismo día que una compra DCA, se ejecutan como dos operaciones separadas — ambas incrementan `btcStack`, `btcBought`, `totalInvested`
- **`costPromedio` no cambia por ventas** — refleja precio promedio histórico de compra
- El DCA base **siempre continúa** independientemente de ventas/recompras

---

## Sección de Resultados

### Stat Boxes (4 cajas, igual que Plan B)

| Caja | ID | Contenido |
|---|---|---|
| BTC Final | `e-btc` | fmtBTC(totalBTC) · sub: `harvestCount + " cosecha(s)"` |
| Costo Promedio Compra | `e-avgprice` | U$S fmt(costPromedio) · sub: "U$S/BTC" |
| Total Invertido | `e-invested` | U$S fmt(totalInvested) · sub: "U$S Bruto DCA" |
| Valor Actual | `e-value` | U$S fmt(currentValue) · sub: "ROI: X%" |

### 📊 Plan A) vs Plan E) — Comparativa

- 3 stat boxes: Plan A BTC · Plan E BTC · Diferencia + ganador
- Gráfico de líneas: curva naranja (#f7931a) Plan E (post-ventas), curva azul (#4a9eff) Plan A
- `spanGaps: true` en ambas líneas
- Ambas curvas muestran `btcStack × precio` (valor de cartera real, Plan E refleja BTC reducido por ventas)

### 🌾 Ciclos de Cosecha (tabla central)

Columnas:
| # | Fecha Venta | Precio Venta | BTC Vendido | U$S Obtenido | % Sobre Costo | Estado | Detalle |
|---|---|---|---|---|---|---|---|

**Estados posibles:**
- `✅ Recomprado` — recompra ejecutada · Detalle = "YYYY-MM-DD a U$S XX.XXX"
- `⏳ Esperando` — U$S en espera de recompra · Detalle = "U$S en espera"
- `🔄 Re-invierte` — fallback ejecutado · Detalle = "Re-invierte en DCA YYYY-MM"

Filas con fondo alterno (igual que otras tablas de la app).

---

## Dashboard — Integración

Agregar Plan E a la tabla comparativa del Dashboard:

```
Plan E) DCA Cosecha | BTC total | Valor U$S | ROI% | Costo Promedio
```

`lastPlanE` usa la misma forma que los demás planes:
```js
lastPlanE = {
  totalBTC,       // btcStack al final
  totalInvested,  // USD invertido total
  avgPrice,       // costPromedio final
  currentValue,   // totalBTC × currentPrice
  roi             // (currentValue - totalInvested) / totalInvested × 100
}
```

---

## Convenciones

- Todo inline en `index.html` — sin archivos .js/.css separados
- Moneda: U$S (nunca USD)
- Números: `fmt()`, `fmtBTC()`, `fmtPct()` existentes
- i18n: agregar claves ES/EN para todos los labels nuevos
- Color Plan E en gráficos: `#f7931a` naranja
- Variable global: `let lastPlanE = null;`
- Función principal: `runPlanE()`

---

## Archivos a Modificar

| Archivo | Cambios |
|---|---|
| `index.html` | Agregar tab E en navbar, HTML de `tab-planE`, función `runPlanE()`, i18n ES+EN, integración Dashboard |

No se crean archivos nuevos.
