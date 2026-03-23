# CLAUDE.md — MatheyBTC-invest-BTC

## Descripción del Proyecto
Tracker y simulador multi-plan de inversión en Bitcoin. Implementa 4 estrategias
en una single-page HTML/JS/CSS app con datos históricos de precios desde Google Sheets.
Deployed en GitHub Pages.

## Cómo Ejecutar
- Abrir `index.html` en browser (carga precios desde Google Sheets CSV al inicio)
- Actualizar precios locales: `python update_prices.py`
- Señal T3-CCI: `python t3cci_signal.py`
- Atajo: doble clic en `iniciar.bat`

## Archivos Clave
| Archivo | Responsabilidad |
|---|---|
| `index.html` | App principal (204KB) — 4 planes, charts, semáforo, backtesting |
| `btc_prices.json` | Precios BTC históricos (127KB) — se copia a DCA-plan |
| `btc_prices.csv` | Mismo dataset en CSV |
| `update_prices.py` | Actualiza btc_prices.json/csv |
| `t3cci_signal.py` | Genera señal de trading T3-CCI |
| `T3-CCI-MatheyBTC.pine` | Indicador TradingView (Pine Script) |
| `DCA_BTC.xlsx` | Spreadsheet de soporte DCA |
| `Colateral.xlsx` | Calculadora de colateral BTC |
| `iniciar.bat` | Abre la app en el browser |
| `Notas/` | Notas de cambios pendientes por plan |

## Stack
Vanilla HTML/CSS/JS · Chart.js 4.4.0 · Python · GitHub Pages · Google Sheets CSV

## Los Cuatro Planes
| Plan | Descripción |
|---|---|
| Plan A | DCA fijo — compras periódicas en USD |
| Plan B | DCA re-compra — vende X% en trigger MA90, recompra lump sum |
| Plan C | Colateral BTC — calculadora de préstamos |
| Plan D | Señales T3-CCI |

## Convenciones de Código
- Todo inline en `index.html` — sin archivos .js/.css separados
- Chart.js para todos los gráficos
- `fmt()`, `fmtBTC()`, `fmtPct()` para formateo numérico
- U$S en lugar de USD en toda la UI
- Title Case en todos los labels
- `getPriceAt(date)` busca el precio más cercano anterior disponible
- Leer `MEMORY.md` al iniciar sesión
