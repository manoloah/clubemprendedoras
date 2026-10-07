/**
 * El Club de las Emprendedoras — waitlist backend (Google Apps Script web app).
 *
 * The landing page (site/) POSTs here in two steps and this script writes
 * one row per person into the bound Google Sheet:
 *   1. Sign-up: name, email, WhatsApp (+ where they came from).
 *   2. Profile (optional modal): the rest of the questions.
 * Setup steps are in README.md next to this file.
 *
 * Design notes:
 * - Writes into your existing headers ("Tu email (aquí te avisamos primero) 📩",
 *   "Timestamp"…). Headers that don't exist yet are added at the end.
 * - One row per email. The /exec URL is public (it's in the page source), so
 *   a repeat post only fills cells that are still empty and never overwrites:
 *   knowing someone's email doesn't let anyone change their answers.
 * - Unknown keys are dropped, values are capped, and formula-looking values
 *   are stored as text.
 * - At most MAX_PER_MINUTE saves per minute across the whole site.
 */

// Tab to write into. Leave "" to use the first tab of the spreadsheet.
const SHEET_NAME = "";

// Page key → column header in the Sheet. Edit the right side if you rename
// a column. Matching ignores case and extra spaces.
const COLUMNS = {
  created_at: "Timestamp",
  email: "Tu email (aquí te avisamos primero) 📩",
  whatsapp: "Tu celular / WhatsApp 📱",
  perfil: "¿Qué te describe mejor?",
  curso_previo: "¿Ya tomaste un taller o curso con nosotras?",
  etapa_idea: "¿Dónde estás hoy con tu idea?",
  freno: "Sé honesta: ¿qué es lo que hoy te frena?",
  interes_2027: "¿Qué te interesaría más para 2027?",
  traba_taller: "¿Qué es lo que más te trabaría durante el taller?",
  horario: "¿Qué ritmo y horario te funcionan mejor?",
  meta_ia: "Cuéntanos en una frase: ¿qué te gustaría construir o lograr con la inteligencia artificial? 👇",
  negocio: "Cuntanos un poco más de ti y de tu negocio",
  instagram: "Tu Instagram o de tu negocio (para avisarte primero)",
  // Added at the end of the sheet the first time they're used if missing:
  nombre: "Tu nombre",
  updated_at: "Actualizado",
  source: "Origen",
  utm_source: "utm_source",
  utm_medium: "utm_medium",
  utm_campaign: "utm_campaign",
  utm_content: "utm_content",
  referrer: "referrer",
};

// Keys the page may send. Anything else is ignored.
const ALLOWED_KEYS = Object.keys(COLUMNS).filter(function (k) {
  return k !== "created_at" && k !== "updated_at";
});

const MAX_LEN = 1000;
const MAX_PER_MINUTE = 30;

function doPost(e) {
  try {
    const data = parseBody_(e);

    // Honeypot: real people never see or fill the "company" field.
    if (data.company) return json_({ ok: true });

    const email = String(data.email || "").trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || email.length > 254) {
      return json_({ ok: false, error: "invalid_email" });
    }

    const row = { email: email };
    ALLOWED_KEYS.forEach(function (key) {
      if (key === "email") return;
      let v = data[key];
      if (Array.isArray(v)) v = v.join(", ");
      if (v == null || String(v).trim() === "") return;
      row[key] = clean_(v);
    });

    const lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      if (!underRateLimit_()) return json_({ ok: false, error: "rate_limited" });
      upsert_(row);
    } finally {
      lock.releaseLock();
    }
    return json_({ ok: true });
  } catch (err) {
    console.error(err);
    return json_({ ok: false, error: "server_error" });
  }
}

// Health check: open the /exec URL in a browser and you should see ok:true.
function doGet() {
  return json_({ ok: true, service: "club-emprendedoras-waitlist" });
}

function upsert_(row) {
  const sheet = getSheet_();
  const keys = ["created_at", "updated_at"].concat(Object.keys(row));
  const colOf = ensureHeaders_(sheet, keys); // key → 1-based column
  const width = sheet.getLastColumn();
  const now = new Date();

  const emailCol = colOf.email;
  const lastRow = sheet.getLastRow();
  let target = -1;
  if (lastRow > 1) {
    const emails = sheet.getRange(2, emailCol, lastRow - 1, 1).getValues();
    for (let i = 0; i < emails.length; i++) {
      if (String(emails[i][0]).trim().toLowerCase() === row.email) { target = i + 2; break; }
    }
  }

  if (target === -1) {
    const values = new Array(width).fill("");
    values[colOf.created_at - 1] = now;
    values[colOf.updated_at - 1] = now;
    Object.keys(row).forEach(function (k) { values[colOf[k] - 1] = row[k]; });
    sheet.appendRow(values);
    return;
  }

  // Existing person: only fill cells that are still empty. Never overwrite.
  const range = sheet.getRange(target, 1, 1, width);
  const values = range.getValues()[0];
  values[colOf.updated_at - 1] = now;
  Object.keys(row).forEach(function (k) {
    const i = colOf[k] - 1;
    if (values[i] === "") values[i] = row[k];
  });
  range.setValues([values]);
}

// Counts saves in the current minute (called while holding the lock).
function underRateLimit_() {
  const cache = CacheService.getScriptCache();
  const key = "saves-" + Math.floor(Date.now() / 60000);
  const count = Number(cache.get(key) || 0);
  if (count >= MAX_PER_MINUTE) return false;
  cache.put(key, String(count + 1), 120);
  return true;
}

function getSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  return (SHEET_NAME && ss.getSheetByName(SHEET_NAME)) || ss.getSheets()[0];
}

function norm_(s) {
  return String(s).replace(/\s+/g, " ").trim().toLowerCase();
}

// Maps each key to its column, adding headers that don't exist yet.
function ensureHeaders_(sheet, keys) {
  const width = Math.max(sheet.getLastColumn(), 1);
  const headers = sheet.getRange(1, 1, 1, width).getValues()[0].map(norm_);
  let used = headers.length;
  while (used > 0 && headers[used - 1] === "") used--;
  const colOf = {};
  keys.forEach(function (k) {
    if (colOf[k]) return;
    const title = COLUMNS[k];
    const idx = headers.indexOf(norm_(title));
    if (idx !== -1) { colOf[k] = idx + 1; return; }
    used++;
    sheet.getRange(1, used).setValue(title).setFontWeight("bold");
    headers[used - 1] = norm_(title);
    colOf[k] = used;
  });
  return colOf;
}

// The page sends JSON as text/plain so the browser skips the CORS preflight
// that Apps Script can't answer.
function parseBody_(e) {
  if (e && e.postData && e.postData.contents) {
    try { return JSON.parse(e.postData.contents); } catch (_) { /* fall through */ }
  }
  return (e && e.parameter) || {};
}

// Trim, cap length, and stop formula injection: values starting with
// = + - @ are stored as text (also keeps the "+" on phone numbers).
function clean_(value) {
  let s = String(value).trim().slice(0, MAX_LEN);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
