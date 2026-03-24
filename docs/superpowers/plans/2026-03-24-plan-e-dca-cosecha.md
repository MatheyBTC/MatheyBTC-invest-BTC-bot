# Plan E) DCA Cosecha — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new "Plan E) DCA Cosecha" tab to index.html that simulates a partial-profit-taking strategy: sells X% of BTC stack when price exceeds own cost average by N%, then rebuys lump-sum when price drops M% from sale price, with a 3-month fallback to DCA if rebuy never triggers.

**Architecture:** Single-file modification — all changes go inline in `index.html`. Follows the exact same pattern as Plan B (tab HTML → i18n keys → JS function → dashboard integration). The algorithm uses a daily loop with fixed monthly check dates calculated from startDate.

**Tech Stack:** Vanilla JS · Chart.js 4.4.0 · existing helpers: `getPriceAt()`, `addDays()`, `daysBetween()`, `getFreqDays()`, `calcDCA()`, `aggregateDCA()`, `fmt()`, `fmtBTC()`, `fmtPct()`, `format_fecha_es()`

---

## File Structure

| File | Change |
|---|---|
| `index.html:297-298` | Add Plan E tab to navbar (before Dashboard tab) |
| `index.html:1322` | Insert `<div id="tab-planE">` HTML after tab-planD closing `</div>` |
| `index.html:1431` | Add `chartE` and `lastPlanE` globals |
| `index.html:1564` | Add Plan E i18n keys in ES section (after Plan D keys) |
| `index.html:1708` | Add Plan E i18n keys in EN section (after Plan D keys) |
| `index.html:3467` | Add Plan E to Dashboard `plans` array |
| `index.html:3643` | Add `runPlanE()` and `exportPlanE()` before `</script>` |

---

## Task 1: Navbar tab + global variables

**Files:**
- Modify: `index.html:298` (navbar)
- Modify: `index.html:1431` (globals)

- [ ] **Step 1: Add Plan E tab to navbar**

Find line 298 in index.html:
```html
    <div class="tab" onclick="showTab('dashboard')" data-i18n="tab-dash">📊 Dashboard</div>
```
Insert BEFORE it:
```html
    <div class="tab" onclick="showTab('planE')" data-i18n="tab-e">Plan E) DCA Cosecha</div>
```

- [ ] **Step 2: Add chartE and lastPlanE globals**

Find line 1431:
```javascript
let chartA = null, chartA_MA = null, chartB = null, chartD = null, chartDash = null;
```
Replace with:
```javascript
let chartA = null, chartA_MA = null, chartB = null, chartD = null, chartDash = null, chartE = null;
```

Find line 1434:
```javascript
let lastPlanA = null, lastPlanB = null, lastPlanC = null, lastPlanD = null;
```
Replace with:
```javascript
let lastPlanA = null, lastPlanB = null, lastPlanC = null, lastPlanD = null, lastPlanE = null;
```

- [ ] **Step 3: Verify in browser**

Open index.html. Should see "Plan E) DCA Cosecha" tab in the navbar. Clicking it shows a blank panel (no content yet — that's expected).

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat(plan-e): add navbar tab and global variables"
```

---

## Task 2: HTML — Tab Panel (inputs + results skeleton)

**Files:**
- Modify: `index.html:1322` (insert after closing `</div>` of tab-planD, before `<div id="tab-dashboard">`)

- [ ] **Step 1: Insert tab-planE HTML**

Find the exact anchor — after line 1322 (`</div>` that closes tab-planD) and before line 1325 (`<div id="tab-dashboard"`). Insert:

```html
<!-- ==================== PLAN E ==================== -->
<div id="tab-planE" class="tab-content">
  <div class="card">
    <h3 data-i18n="e-params-title">⚙️ Parámetros DCA Cosecha</h3>
    <div class="form-row">
      <div class="form-group">
        <label data-i18n="a-amount-label">Monto por Compra (U$S)</label>
        <input type="number" id="e-amount" value="100" min="1">
      </div>
      <div class="form-group">
        <label data-i18n="a-freq-label">Frecuencia</label>
        <select id="e-freq">
          <option value="1" data-i18n="freq-diaria">Diaria</option>
          <option value="7" data-i18n="freq-semanal">Semanal</option>
          <option value="14" data-i18n="freq-bisemanal">Bisemanal</option>
          <option value="30" selected data-i18n="freq-mensual">Mensual</option>
        </select>
      </div>
      <div class="form-group">
        <label data-i18n="a-start-label">Fecha Inicio</label>
        <input type="date" id="e-start" value="2020-01-01">
      </div>
      <div class="form-group">
        <label data-i18n="a-end-label">Fecha Fin</label>
        <input type="date" id="e-end">
      </div>
      <div class="form-group">
        <label data-i18n="e-umbral-venta-label">Vender Cuando Precio Sube X% Sobre Mi Costo Promedio</label>
        <input type="number" id="e-umbral-venta" value="50" min="1" max="500">
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:6px;">
          <button onclick="document.getElementById('e-umbral-venta').value=25" style="background:#ef4444;color:#fff;padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:12px;font-weight:700;">25%</button>
          <button onclick="document.getElementById('e-umbral-venta').value=50" style="background:#f97316;color:#fff;padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:12px;font-weight:700;">50%</button>
          <button onclick="document.getElementById('e-umbral-venta').value=75" style="background:#facc15;color:#000;padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:12px;font-weight:700;">75%</button>
          <button onclick="document.getElementById('e-umbral-venta').value=100" style="background:#4ade80;color:#000;padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:12px;font-weight:700;">100%</button>
        </div>
      </div>
      <div class="form-group">
        <label data-i18n="e-pct-venta-label">Vender % del Stack</label>
        <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">
          <button onclick="document.getElementById('e-pct-venta').value=5" style="background:#4ade80;color:#000;padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:12px">5%</button>
          <button onclick="document.getElementById('e-pct-venta').value=10" style="background:#facc15;color:#000;padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:12px">10%</button>
          <button onclick="document.getElementById('e-pct-venta').value=15" style="background:#ef4444;color:#fff;padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:12px">15%</button>
          <input type="number" id="e-pct-venta" value="10" min="1" max="100" style="width:65px">
        </div>
      </div>
      <div class="form-group">
        <label data-i18n="e-umbral-recompra-label">Recomprar Cuando Precio Baja X% Desde Precio de Venta</label>
        <input type="number" id="e-umbral-recompra" value="20" min="1" max="100">
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:6px;">
          <button onclick="document.getElementById('e-umbral-recompra').value=5" style="background:#ef4444;color:#fff;padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:12px;font-weight:700;">5%</button>
          <button onclick="document.getElementById('e-umbral-recompra').value=10" style="background:#f97316;color:#fff;padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:12px;font-weight:700;">10%</button>
          <button onclick="document.getElementById('e-umbral-recompra').value=15" style="background:#facc15;color:#000;padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:12px;font-weight:700;">15%</button>
          <button onclick="document.getElementById('e-umbral-recompra').value=25" style="background:#4ade80;color:#000;padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:12px;font-weight:700;">25%</button>
        </div>
      </div>
      <div class="form-group" style="justify-content:flex-end">
        <button class="btn" onclick="runPlanE()" data-i18n="calcular">Calcular</button>
      </div>
      <div class="form-group" style="justify-content:flex-end">
        <button class="btn-outline" onclick="exportPlanE()">📥 Excel</button>
      </div>
    </div>
  </div>

  <div id="e-results" style="display:none">
    <div class="grid-4 mb-16">
      <div class="stat-box">
        <div class="label" data-i18n="e-btc-label">BTC Final</div>
        <div class="value" id="e-btc">—</div>
        <div class="sub" id="e-harvests">— cosecha(s)</div>
      </div>
      <div class="stat-box">
        <div class="label" data-i18n="a-avgprice-label">Precio Promedio Compra</div>
        <div class="value" id="e-avgprice">—</div>
        <div class="sub">U$S/BTC</div>
      </div>
      <div class="stat-box">
        <div class="label" data-i18n="a-invested-label">Total Invertido</div>
        <div class="value" id="e-invested">—</div>
        <div class="sub">U$S Bruto DCA</div>
      </div>
      <div class="stat-box green">
        <div class="label" data-i18n="a-value-label">Valor Actual</div>
        <div class="value" id="e-value">—</div>
        <div class="sub" id="e-roi">ROI: —</div>
      </div>
    </div>

    <div class="card">
      <h3 data-i18n="e-vs-title">📊 Plan A) vs Plan E) — Comparativa</h3>
      <div class="grid-3 mb-16">
        <div class="stat-box" style="border-color:#4a9eff;background:rgba(74,158,255,0.07)">
          <div class="label" style="color:#4a9eff;font-size:13px;font-weight:600" data-i18n="tab-a">Plan A) DCA Fijo</div>
          <div class="value" id="e-vs-a-btc">—</div>
          <div class="sub" data-i18n="b-btc-acum">BTC (Acumulado)</div>
        </div>
        <div class="stat-box" style="border-color:#f7931a;background:rgba(247,147,26,0.07)">
          <div class="label" style="color:#f7931a;font-size:13px;font-weight:600" data-i18n="tab-e">Plan E) DCA Cosecha</div>
          <div class="value" id="e-vs-e-btc">—</div>
          <div class="sub" data-i18n="b-btc-acum">BTC (Acumulado)</div>
        </div>
        <div class="stat-box green">
          <div class="label" data-i18n="b-diferencia">Diferencia</div>
          <div class="value" id="e-vs-diff">—</div>
          <div class="sub" id="e-vs-winner">—</div>
        </div>
      </div>
      <div class="chart-wrap"><canvas id="chartE"></canvas></div>
    </div>

    <div class="card">
      <h3 data-i18n="e-ciclos-title">🌾 Ciclos de Cosecha</h3>
      <table class="tbl">
        <thead><tr>
          <th>#</th>
          <th data-i18n="th-fecha">Fecha Venta</th>
          <th class="num" data-i18n="th-precio-btc">Precio Venta</th>
          <th class="num" data-i18n="th-btc-vendido">BTC Vendido</th>
          <th class="num" data-i18n="th-usd-obtenido">U$S Obtenido</th>
          <th class="num" data-i18n="e-th-pct-costo">% Sobre Costo</th>
          <th data-i18n="e-th-estado">Estado</th>
          <th data-i18n="e-th-detalle">Detalle</th>
        </tr></thead>
        <tbody id="e-cycles-body"></tbody>
      </table>
    </div>
  </div>
</div>
```

- [ ] **Step 2: Set default end date on load**

In the existing `window.onload` or date-init block (search for `b-end` or `a-end` date initialization), add the same pattern for `e-end`:

Find the block that sets `b-end` value (search: `document.getElementById('b-end').value`). Add after it:
```javascript
document.getElementById('e-end').value = today;
```
(where `today` is the existing variable used for `b-end`)

- [ ] **Step 3: Verify in browser**

Open index.html → click Plan E tab. Should see full form with all inputs and quick-buttons. Clicking Calcular should show an alert "Primero cargá los precios históricos." (function not yet implemented — expected).

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat(plan-e): add tab HTML with inputs and results skeleton"
```

---

## Task 3: i18n Keys (ES + EN)

**Files:**
- Modify: `index.html:1564` (after `'d-pnl-acum'` in ES section)
- Modify: `index.html:1708` (after `'d-pnl-acum'` in EN section)

- [ ] **Step 1: Add ES keys**

Find in the `es:` block (around line 1564):
```javascript
    'd-pnl-acum': 'P&L Acum.',
    // Dashboard
```
Insert BETWEEN those two lines:
```javascript
    // Plan E
    'tab-e': 'Plan E) DCA Cosecha',
    'e-params-title': '⚙️ Parámetros DCA Cosecha',
    'e-umbral-venta-label': 'Vender Cuando Precio Sube X% Sobre Mi Costo Promedio',
    'e-pct-venta-label': 'Vender % del Stack',
    'e-umbral-recompra-label': 'Recomprar Cuando Precio Baja X% Desde Precio de Venta',
    'e-btc-label': 'BTC Final',
    'e-vs-title': '📊 Plan A) vs Plan E) — Comparativa',
    'e-ciclos-title': '🌾 Ciclos de Cosecha',
    'e-th-pct-costo': '% Sobre Costo',
    'e-th-estado': 'Estado',
    'e-th-detalle': 'Detalle',
```

- [ ] **Step 2: Add EN keys**

Find in the `en:` block (around line 1708):
```javascript
    'd-pnl-acum': 'Cumul. P&L',
    // Dashboard
```
Insert BETWEEN those two lines:
```javascript
    // Plan E
    'tab-e': 'Plan E) DCA Harvest',
    'e-params-title': '⚙️ DCA Harvest Parameters',
    'e-umbral-venta-label': 'Sell When Price Rises X% Above My Cost Average',
    'e-pct-venta-label': 'Sell % of Stack',
    'e-umbral-recompra-label': 'Rebuy When Price Drops X% From Sale Price',
    'e-btc-label': 'Final BTC',
    'e-vs-title': '📊 Plan A) vs Plan E) — Comparison',
    'e-ciclos-title': '🌾 Harvest Cycles',
    'e-th-pct-costo': '% Above Cost',
    'e-th-estado': 'Status',
    'e-th-detalle': 'Detail',
```

- [ ] **Step 3: Verify**

Open index.html → toggle language (if there's a language button). Plan E tab label should change between "Plan E) DCA Cosecha" and "Plan E) DCA Harvest".

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat(plan-e): add i18n keys ES and EN"
```

---

## Task 4: Core Algorithm — runPlanE()

**Files:**
- Modify: `index.html:3643` (add before `</script>`)

- [ ] **Step 1: Add runPlanE() function**

Find the very end of the `<script>` block (just before `</script>`):
```javascript
}
</script>
```
Insert the full `runPlanE()` function before `</script>`:

```javascript
function setEUmbralVenta(v) { document.getElementById('e-umbral-venta').value = v; }
function setEPctVenta(v)    { document.getElementById('e-pct-venta').value = v; }
function setEUmbralRecompra(v) { document.getElementById('e-umbral-recompra').value = v; }

function runPlanE() {
  if (!priceHistory.length) { alert('Primero cargá los precios históricos.'); return; }

  const amount          = parseFloat(document.getElementById('e-amount').value);
  const freqDays        = getFreqDays(document.getElementById('e-freq').value);
  const startDate       = document.getElementById('e-start').value;
  const endDate         = document.getElementById('e-end').value;
  const umbralVenta     = parseFloat(document.getElementById('e-umbral-venta').value) / 100;
  const pctVenta        = parseFloat(document.getElementById('e-pct-venta').value) / 100;
  const umbralRecompra  = parseFloat(document.getElementById('e-umbral-recompra').value) / 100;

  // --- State ---
  let btcStack      = 0;
  let btcBought     = 0;
  let totalInvested = 0;
  let costPromedio  = 0;
  let usdEspera     = 0;
  let precioVenta   = 0;
  let mesesEspera   = 0;
  let lastSaleDate  = null;
  let harvestCount  = 0;
  const fallbackQueue = []; // { date, amount }
  const cycles        = [];
  const equity        = [];

  // Fixed monthly check dates from startDate (not reset by sales)
  const checkDates = new Set();
  let cd = addDays(startDate, 30);
  while (cd <= endDate) { checkDates.add(cd); cd = addDays(cd, 30); }

  let nextBuyDate = startDate;
  let d = startDate;

  while (d <= endDate) {
    const price = getPriceAt(d);

    // 1. Process fallback queue (synthetic DCA instalments)
    for (let i = fallbackQueue.length - 1; i >= 0; i--) {
      const q = fallbackQueue[i];
      if (q.date <= d && price > 0) {
        const btc = q.amount / price;
        btcStack      += btc;
        btcBought     += btc;
        totalInvested += q.amount;
        costPromedio   = btcBought > 0 ? totalInvested / btcBought : 0;
        fallbackQueue.splice(i, 1);
      }
    }

    // 2. DCA base purchase
    if (d >= nextBuyDate && price > 0) {
      const btc = amount / price;
      btcStack      += btc;
      btcBought     += btc;
      totalInvested += amount;
      costPromedio   = btcBought > 0 ? totalInvested / btcBought : 0;
      nextBuyDate    = addDays(d, freqDays);
    }

    // 3. Monthly check (fixed clock from startDate)
    if (checkDates.has(d)) {
      if (usdEspera > 0 && price > 0) {
        // Check rebuy condition
        if (price <= precioVenta * (1 - umbralRecompra)) {
          // RECOMPRA lump sum
          const btc = usdEspera / price;
          btcStack      += btc;
          btcBought     += btc;
          totalInvested += usdEspera;
          costPromedio   = btcBought > 0 ? totalInvested / btcBought : 0;
          const cycle = cycles[cycles.length - 1];
          if (cycle) {
            cycle.estado  = '✅ Recomprado';
            cycle.detalle = d + ' a U$S ' + fmt(price, 0);
          }
          harvestCount++;
          usdEspera = 0; precioVenta = 0; mesesEspera = 0;
        } else {
          mesesEspera++;
          // Fallback: after 3 checks AND at least 90 days since sale
          if (mesesEspera >= 3 && lastSaleDate && daysBetween(lastSaleDate, d) >= 90) {
            const cuota = usdEspera / 3;
            fallbackQueue.push({ date: addDays(d, 30), amount: cuota });
            fallbackQueue.push({ date: addDays(d, 60), amount: cuota });
            fallbackQueue.push({ date: addDays(d, 90), amount: cuota });
            const cycle = cycles[cycles.length - 1];
            if (cycle) {
              cycle.estado  = '🔄 Re-invierte';
              cycle.detalle = 'Re-invierte en DCA ' + d.substring(0, 7);
            }
            harvestCount++;
            usdEspera = 0; precioVenta = 0; mesesEspera = 0;
          }
        }
      } else if (usdEspera === 0 && btcStack > 0 && price > 0 && costPromedio > 0) {
        // Check sale condition
        const cooldownOk = !lastSaleDate || daysBetween(lastSaleDate, d) >= 30;
        if (cooldownOk && price > costPromedio * (1 + umbralVenta)) {
          const btcToSell    = btcStack * pctVenta;
          const usdObtenido  = btcToSell * price;
          const pctSobreCosto = ((price / costPromedio) - 1) * 100;
          btcStack    -= btcToSell;
          usdEspera    = usdObtenido;
          precioVenta  = price;
          lastSaleDate = d;
          mesesEspera  = 0;
          cycles.push({
            id: cycles.length + 1,
            fecha:        d,
            precioVenta:  price,
            btcVendido:   btcToSell,
            usdObtenido,
            pctSobreCosto,
            estado:       '⏳ Esperando',
            detalle:      'U$S en espera',
          });
        }
      }
    }

    equity.push({ date: d, btc: btcStack, value: btcStack * price });
    d = addDays(d, 1);
  }

  // Use price at endDate for historical accuracy (not live currentPrice)
  const endPrice     = getPriceAt(endDate);
  const currentValue = btcStack * endPrice;
  const roi          = totalInvested > 0 ? ((currentValue - totalInvested) / totalInvested) * 100 : 0;

  lastPlanE = { totalBTC: btcStack, totalInvested, avgPrice: costPromedio, currentValue, roi, cycles };

  // Plan A comparison (same params)
  const purchasesA = calcDCA(startDate, endDate, amount, freqDays);
  const aggA       = aggregateDCA(purchasesA);

  // --- Render stat boxes ---
  document.getElementById('e-btc').textContent      = fmtBTC(btcStack);
  document.getElementById('e-harvests').textContent = harvestCount + ' cosecha(s)';
  document.getElementById('e-avgprice').textContent = 'U$S ' + fmt(costPromedio, 0);
  document.getElementById('e-invested').textContent = 'U$S ' + fmt(totalInvested, 0);
  document.getElementById('e-value').textContent    = 'U$S ' + fmt(currentValue, 0);
  document.getElementById('e-roi').textContent      = 'ROI: ' + fmtPct(roi);

  // --- Comparativa vs Plan A ---
  document.getElementById('e-vs-a-btc').textContent  = fmtBTC(aggA.totalBTC);
  document.getElementById('e-vs-e-btc').textContent  = fmtBTC(btcStack);
  const diff = btcStack - aggA.totalBTC;
  document.getElementById('e-vs-diff').textContent   = fmtBTC(Math.abs(diff));
  const winner = document.getElementById('e-vs-winner');
  winner.textContent = diff >= 0 ? 'Plan E) es Superior' : 'Plan A) es Superior';
  winner.style.color = diff >= 0 ? 'var(--green)' : 'var(--yellow)';

  // --- Chart E ---
  const ctx = document.getElementById('chartE').getContext('2d');
  if (chartE) chartE.destroy();
  const step     = Math.max(1, Math.floor(equity.length / 300));
  const filtered = equity.filter((_, i) => i % step === 0);
  const planAMap = {};
  aggA.equity.forEach(e => { planAMap[e.date] = e.value; });
  chartE = new Chart(ctx, {
    type: 'line',
    data: {
      labels: filtered.map(e => e.date),
      datasets: [
        { label: 'Plan E) DCA Cosecha', data: filtered.map(e => e.value),
          borderColor: '#f7931a', pointRadius: 0, tension: 0.3, fill: false, spanGaps: true },
        { label: 'Plan A) DCA Fijo', data: filtered.map(e => planAMap[e.date] || null),
          borderColor: '#4a9eff', pointRadius: 0, tension: 0.3, fill: false, spanGaps: true },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#e0e0e0', font: { size: 13 } } } },
      scales: {
        x: { ticks: { color: '#888', maxTicksLimit: 12 }, grid: { color: '#222' } },
        y: { ticks: { color: '#888', callback: v => '$' + fmt(v, 0) }, grid: { color: '#222' } }
      }
    }
  });

  // --- Cycles table ---
  const tbody = document.getElementById('e-cycles-body');
  tbody.innerHTML = '';
  if (cycles.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="color:var(--text2);text-align:center;padding:16px;">Sin cosechas en el período</td></tr>';
  } else {
    cycles.forEach((c, i) => {
      const tr = document.createElement('tr');
      tr.style.background = i % 2 === 0 ? 'var(--bg3)' : 'transparent';
      tr.innerHTML = `
        <td>${c.id}</td>
        <td>${c.fecha}</td>
        <td class="num">U$S ${fmt(c.precioVenta, 0)}</td>
        <td class="num">${fmtBTC(c.btcVendido)}</td>
        <td class="num">U$S ${fmt(c.usdObtenido, 0)}</td>
        <td class="num">${fmtPct(c.pctSobreCosto)}</td>
        <td>${c.estado}</td>
        <td style="font-size:12px;color:var(--text2)">${c.detalle}</td>`;
      tbody.appendChild(tr);
    });
  }

  document.getElementById('e-results').style.display = 'block';
}
```

- [ ] **Step 2: Verify algorithm in browser**

Load prices → go to Plan E → set dates 2020-01-01 to 2024-01-01, defaults (50%/10%/20%) → click Calcular.

Expected:
- Stat boxes show BTC, cost average, invested, value, ROI
- Chart shows two lines (orange Plan E, blue Plan A)
- Ciclos de Cosecha table shows at least one row (BTC had big run-ups in this period)
- "Sin cosechas" only if no trigger fired (check dates and thresholds)

- [ ] **Step 3: Test edge case — no triggers**

Set umbral-venta to 500% → Calcular. Expected: "Sin cosechas en el período" table message. Stat boxes should match Plan A exactly (no sells happened).

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat(plan-e): implement runPlanE() algorithm with harvest cycles"
```

---

## Task 5: Dashboard Integration

**Files:**
- Modify: `index.html:3467` (plans array in runDashboard)

- [ ] **Step 1: Add Plan E to Dashboard plans array**

Find in `runDashboard()` (around line 3467):
```javascript
    { name: 'Plan D) Trading', data: lastPlanD ? { totalBTC: lastPlanD.currentBTC, totalInvested: lastPlanD.netInvested, avgPrice: lastPlanD.netInvested / lastPlanD.currentBTC, currentValue: lastPlanD.currentVal, roi: lastPlanD.pnlPct } : null },
  ];
```
Replace the `];` at the end with:
```javascript
    { name: 'Plan D) Trading', data: lastPlanD ? { totalBTC: lastPlanD.currentBTC, totalInvested: lastPlanD.netInvested, avgPrice: lastPlanD.netInvested / lastPlanD.currentBTC, currentValue: lastPlanD.currentVal, roi: lastPlanD.pnlPct } : null },
    { name: 'Plan E) DCA Cosecha', data: lastPlanE },
  ];
```

- [ ] **Step 2: Verify in browser**

Calculate Plan E → go to Dashboard → click Calcular. Plan E row should appear in the "Resumen de Todos los Planes" table. If Plan E hasn't been calculated yet, it shows "Sin calcular — ir al plan y ejecutar primero".

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat(plan-e): add to Dashboard summary table"
```

---

## Task 6: Export to Excel

**Files:**
- Modify: `index.html:3643` (add after runPlanE, before `</script>`)

- [ ] **Step 1: Add exportPlanE() function**

Add after the closing `}` of `runPlanE()`:

```javascript
function exportPlanE() {
  if (!lastPlanE) { alert('Calculá el Plan E primero.'); return; }
  const wb = XLSX.utils.book_new();

  // Summary sheet
  const summary = [
    ['Plan E) DCA Cosecha — Resumen'],
    ['BTC Final', lastPlanE.totalBTC],
    ['Costo Promedio (U$S)', lastPlanE.avgPrice],
    ['Total Invertido (U$S)', lastPlanE.totalInvested],
    ['Valor Actual (U$S)', lastPlanE.currentValue],
    ['ROI (%)', lastPlanE.roi],
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(summary), 'Resumen');

  // Cycles sheet
  const cycleRows = [['#', 'Fecha Venta', 'Precio Venta', 'BTC Vendido', 'U$S Obtenido', '% Sobre Costo', 'Estado', 'Detalle']];
  (lastPlanE.cycles || []).forEach(c => {
    cycleRows.push([c.id, c.fecha, c.precioVenta, c.btcVendido, c.usdObtenido, c.pctSobreCosto, c.estado, c.detalle]);
  });
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(cycleRows), 'Ciclos de Cosecha');

  XLSX.writeFile(wb, 'MatheyBTC_PlanE.xlsx');
}
```

- [ ] **Step 2: Verify**

Calculate Plan E → click 📥 Excel. Should download `MatheyBTC_PlanE.xlsx` with summary data. Clicking without calculating first shows alert.

- [ ] **Step 3: Final commit**

```bash
git add index.html
git commit -m "feat(plan-e): add Excel export"
git push
```

---

## Task 7: Replicate to DCA-plan project

**Files:**
- Modify: `D:/claude/Projects/MatheyBTC-DCA-plan/index.html`

The DCA-plan project is kept in sync with invest-BTC. Apply all the same changes (Tasks 1–6) to `D:/claude/Projects/MatheyBTC-DCA-plan/index.html`.

Check if DCA-plan has the same structure:
```bash
grep -n "tab-planD\|tab-dashboard\|lastPlanD" D:/claude/Projects/MatheyBTC-DCA-plan/index.html | head -10
```

Apply identical changes. Then:
```bash
cd D:/claude/Projects/MatheyBTC-DCA-plan
git add index.html
git commit -m "feat(plan-e): add DCA Cosecha tab (sync with invest-BTC)"
git push
```

---

## Notes for implementor

- `getFreqDays(val)` exists at line 2005 — takes the select value string and returns integer days
- `addDays(dateStr, n)` at line 2013 — returns new date string
- `daysBetween(a, b)` at line 2019 — returns integer days between two date strings
- `getPriceAt(dateStr)` at line 1990 — returns closest price ≤ date from priceHistory
- `calcDCA(start, end, amount, freqDays)` at line 2026 — returns purchase array
- `aggregateDCA(purchases)` at line 2039 — returns `{ totalBTC, totalInvested, avgPrice, equity, ... }`
- `fmt(n, decimals)`, `fmtBTC(n)`, `fmtPct(n)` — formatters
- `currentPrice` — global, set when prices load
- `priceHistory` — global array of `[dateStr, price]`
- Chart color conventions: Plan A = `#4a9eff`, Plan B = `#f7931a`, Plan E = `#f7931a` (same orange as BTC)
