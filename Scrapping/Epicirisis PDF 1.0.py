# -*- coding: utf-8 -*-
import os, time, base64, re, tempfile
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# ===================== CONFIG =====================

LOGIN_URL = 'https://comunidad.fundaciontrauma.org.ar/Account/Login'

APP_TILE_ALTS = [
    'Registro de Cadera',
    'Registro de Fractura de Caderas',
    'Registro de Caderas'
]

ORG_VALUE = '2116'                     
HEADLESS = False

USERNAME = os.getenv('FT_USER', 'xxxxxxxxxxxx') # Cambiar por tus credenciales
PASSWORD = os.getenv('FT_PASS', 'xxxxxxxxx') # Cambiar por tus credenciales

START_HECHO_ID = 5788
END_HECHO_ID   = 5788

OUTPUT_EXCEL   = r'C:\Users\herna\Downloads\Mapeo_Epicrisis.xlsx' # Cambiar por tu ruta
OUTPUT_PDF_DIR = r'C:\Users\herna\Downloads\PDFs_Epicrisis'
os.makedirs(OUTPUT_PDF_DIR, exist_ok=True)

# variable global para guardar el nombre de institución
ORG_NAME = '—'

# ==================================================

def build_driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument('--headless=new')
    opts.add_argument('--window-size=1440,1800')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-software-rasterizer')

    drv = webdriver.Chrome(options=opts)
    drv.set_page_load_timeout(240)
    drv.implicitly_wait(8)
    try:
        drv.command_executor._client_config.timeout = 300
    except Exception:
        pass
    return drv

def safe_print_to_pdf(driver, params=None, retries=2, wait_between=1.0):
    if params is None:
        params = {}
    last_err = None
    for _ in range(retries):
        try:
            return driver.execute_cdp_cmd("Page.printToPDF", params)["data"]
        except Exception as e:
            last_err = e
            time.sleep(wait_between)
            try:
                driver.get("about:blank")
            except Exception:
                pass
    raise last_err

def wait_any_present(driver, css_list, timeout=30):
    end = time.time() + timeout
    last_exc = None
    while time.time() < end:
        for sel in css_list:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el.is_displayed():
                    return sel, el
            except Exception as e:
                last_exc = e
        time.sleep(0.25)
    raise TimeoutException(f"No apareció ninguno de: {css_list}. Último error: {last_exc}")

def iniciar_sesion(driver):
    global ORG_NAME

    driver.get(LOGIN_URL)

    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input,form,button")))
    for css in ['#Username', 'input[name="Username"]', 'input[name="username"]', 'input[type="text"]']:
        els = driver.find_elements(By.CSS_SELECTOR, css)
        if els:
            els[0].clear(); els[0].send_keys(USERNAME); break

    for css in ['#Password', 'input[name="Password"]', 'input[name="password"]', 'input[type="password"]']:
        els = driver.find_elements(By.CSS_SELECTOR, css)
        if els:
            els[0].clear(); els[0].send_keys(PASSWORD); break

    for css in ['input[type="submit"]', 'button[type="submit"]']:
        btns = driver.find_elements(By.CSS_SELECTOR, css)
        if btns:
            btns[0].click(); break

    sel, el = wait_any_present(
        driver,
        ['#ddlOrganizaciones'] + [f'img[alt="{alt}"]' for alt in APP_TILE_ALTS],
        timeout=45
    )
    if sel == '#ddlOrganizaciones':
        select_element = Select(driver.find_element(By.ID, 'ddlOrganizaciones'))
        select_element.select_by_value(ORG_VALUE)
        try:
            ORG_NAME = select_element.first_selected_option.text.strip()
        except Exception:
            ORG_NAME = '—'

        for css in ['input[type="submit"]', '.login-btn']:
            btns = driver.find_elements(By.CSS_SELECTOR, css)
            if btns:
                btns[0].click(); break
        for alt in APP_TILE_ALTS:
            try:
                tile = WebDriverWait(driver, 40).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f'img[alt="{alt}"]'))
                )
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tile)
                driver.execute_script("arguments[0].click();", tile)
                return ORG_NAME
            except TimeoutException:
                continue
        raise TimeoutException("No encontré ningún tile de Cadera tras seleccionar institución.")
    else:
        ORG_NAME = ORG_NAME or '—'
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        driver.execute_script("arguments[0].click();", el)
        return ORG_NAME

def get_cur_from_body(driver):
    try:
        txt = driver.find_element(By.TAG_NAME, 'body').text
    except Exception:
        txt = driver.find_element(By.TAG_NAME, 'body').text
    m = re.search(r'CUR\s*[:：]?\s*([0-9.\-]+)', txt)
    return m.group(1).strip() if m else ''

def click_epicrisis(driver):
    try:
        btn = driver.find_element(By.CSS_SELECTOR, "button[data-btn-type='resumen_hecho']")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        btn.click()
        return True
    except Exception:
        pass
    try:
        btn = driver.find_element(By.CSS_SELECTOR, "button[onclick*='solicitarResumen(true)']")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        btn.click()
        return True
    except Exception:
        pass
    js = """
      const nodes = Array.from(document.querySelectorAll('button,a,.btn,[role="button"]'));
      const hit = nodes.find(n => /EPICRISIS\\s+DEL\\s+HECHO/i.test(n.textContent||''));
      if (hit){ hit.scrollIntoView({block:'center'}); hit.click(); return true; }
      return false;
    """
    try:
        return bool(driver.execute_script(js))
    except Exception:
        return False

def wait_epicrisis_modal(driver, timeout=20):
    end = time.time() + timeout
    selectors = [
        ".modal.show .modal-body",
        ".modal.in .modal-body",
        ".fancybox-opened .modal-body",
        ".fancybox-wrap .modal-body",
        ".modal.show", ".modal.in", ".fancybox-opened", ".fancybox-wrap"
    ]
    while time.time() < end:
        for sel in selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el.is_displayed():
                    return el
            except Exception:
                pass
        time.sleep(0.25)
    return None

def clean_and_extract_modal_html(driver, modal_el):
    js = r"""
    const modal = arguments[0];
    const clone = modal.cloneNode(true);
    const norm = s => (s||'').replace(/\s+/g,' ').trim().toLowerCase();
    const patterns = [
      '¿está por registrar un paciente mayor o igual a 60 años',
      '¿tiene documento?'
    ];
    const rows = clone.querySelectorAll('.row');
    rows.forEach(row => {
      const lab = row.querySelector('label');
      const txt = norm(lab ? lab.textContent : row.textContent);
      if (patterns.some(p => txt.startsWith(p))) row.remove();
    });
    clone.querySelectorAll('input[type="checkbox"], input[type="radio"]').forEach(i => i.remove());
    return clone.outerHTML;
    """
    try:
        return driver.execute_script(js, modal_el)
    except Exception:
        try:
            return driver.execute_script("return arguments[0].outerHTML;", modal_el)
        except Exception:
            return ""

# ---------- RENDER DEL HTML A EXPORTAR (sin footer propio) ----------
def render_modal_html_standalone(modal_html, cur, org_name, username):
    """
    - Fuente general Montserrat 11pt
    - Encabezado con EPICRISIS, CUR y Nombre de institución
    - SIN footer propio: el disclaimer va en el footer nativo de Chrome
    """
    CSS = """
    @page { size: A4; margin: 18mm 14mm 42mm 14mm; } /* bottom grande para el footer nativo */
    *{ box-sizing:border-box; }
    body{
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
      font-family: 'Montserrat', Segoe UI, Roboto, Arial, sans-serif;
      font-size: 11pt; line-height: 1.35; margin:0; background:#fff;
    }
    .wrap{ padding: 8px 0 0; }
    .hdr{ display:flex; flex-direction:column; gap:4px; margin-bottom:10px; }
    .title{ font-size: 18pt; font-weight:700; color:#0d47a1; }
    .meta{ display:flex; gap:16px; flex-wrap:wrap; color:#111827; font-weight:600; }
    .meta .label{ color:#5f6b7a; font-weight:600; margin-right:6px; }
    hr{ border:none; border-top:1px solid #e6ebf2; margin:10px 0; }
    label{ color:#5f6b7a; font-weight:600; }
    .row{ display:flex; flex-wrap:wrap; margin:5px 0; }
    .col-md-3{ width:30%; padding-right:10px; }
    .col-md-9{ width:70%; }
    ul{ margin:4px 0 4px 16px; }
    table{ width:100%; border-collapse:collapse; margin:6px 0; font-size:10pt;}
    th,td{ border:1px solid #e6ebf2; padding:6px 8px; text-align:left; }
    .panel-heading{ font-weight:700; color:#0d47a1; margin:6px 0; }
    """
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>EPICRISIS DEL HECHO {cur or ''}</title>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
  <style>{CSS}</style>
</head>
<body>
  <div class="wrap">
    <div class="hdr">
      <div class="title">EPICRISIS DEL HECHO</div>
      <div class="meta">
        <div><span class="label">CUR:</span> {cur or '—'}</div>
        <div><span class="label">Institución:</span> {org_name or '—'}</div>
      </div>
      <hr>
    </div>
    {modal_html}
  </div>
</body>
</html>"""

def print_modal_to_pdf(driver, modal_html, out_pdf_path, cur, org_name):
    """
    Imprime el HTML stand-alone y agrega footer nativo (Opción B corregida):
    - Línea superior tenue
    - Separación visible antes de “Aviso de Confidencialidad”
    - Texto 7pt con buen interlineado
    - “Documento generado por … · Institución …” a la izquierda
      y paginación “Página X / Y” a la derecha.
    """
    html_doc = render_modal_html_standalone(modal_html, cur, org_name, USERNAME)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html_doc)
        temp_html = f.name
    try:
        driver.get("file://" + temp_html)

        disclaimer = (
            "Este documento contiene información confidencial de pacientes incluidos en el Registro de Fracturas de Cadera®. "
            "Su uso está restringido exclusivamente al usuario que lo generó, quien se compromete a no divulgar, copiar ni distribuir la información contenida en el mismo.\n"
            "Si usted no es el destinatario, queda estrictamente prohibida cualquier forma de utilización de este documento. "
            "En caso de haber accedido al mismo por error, notifique de inmediato al responsable designado al final de este documento.\n"
            "El tratamiento de la información contenida se encuentra regulado por la Ley N.º 25.326 de Protección de los Datos Personales de la República Argentina, "
            "que establece sanciones civiles, administrativas y penales en caso de uso indebido o divulgación no autorizada de datos sensibles."
        )
        ts = time.strftime('%d/%m/%Y %H:%M')

        # ===== Footer Opción B (corregida) =====
        footer_tpl = f"""
        <div style="width:100%; font-family:'Montserrat',Segoe UI,Roboto,Arial,sans-serif;
                    font-size:7pt; line-height:1.35; color:#374151; padding:0 8px 0 8px;
                    border-top:1px solid #e5e7eb;">
          <!-- separador visual entre la línea y el título -->
          <div style="height:6px;"></div>

          <div style="font-weight:700; font-style:italic; margin-bottom:2px;">Aviso de Confidencialidad</div>
          <div style="white-space:pre-line; text-align:left;">{disclaimer}</div>

          <div style="margin-top:6px; display:flex; align-items:center; justify-content:space-between;
                      font-style:italic;">
            <div>Documento generado por {USERNAME} el {ts} · Institución: {org_name}</div>
            <div>Página <span class="pageNumber"></span> / <span class="totalPages"></span></div>
          </div>
        </div>
        """

        params = {
            "printBackground": True,
            "paperWidth": 8.27, "paperHeight": 11.69,     # A4
            # margen inferior amplio para que no haya solape con el contenido
            "marginTop": 0.60, "marginBottom": 1.70, "marginLeft": 0.55, "marginRight": 0.55,
            "displayHeaderFooter": True,
            "headerTemplate": "<div></div>",
            "footerTemplate": footer_tpl
        }
        pdf_b64 = driver.execute_cdp_cmd("Page.printToPDF", params)["data"]
        with open(out_pdf_path, "wb") as f:
            f.write(base64.b64decode(pdf_b64))
    finally:
        try:
            os.remove(temp_html)
        except Exception:
            pass


def procesar_hecho_epicrisis(driver, hecho_id):
    url = f"https://cadera.fundaciontrauma.org.ar/Hecho?id={hecho_id}"
    driver.get(url)
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    cur = get_cur_from_body(driver)
    cur_slug = cur.replace('.', '').replace('-', '') if cur else str(hecho_id)

    if not click_epicrisis(driver):
        raise RuntimeError("No se pudo clickear 'EPICRISIS DEL HECHO'.")

    modal_el = wait_epicrisis_modal(driver, timeout=25)
    if not modal_el:
        pdf_fallback = os.path.join(OUTPUT_PDF_DIR, f"Epicrisis_FALLBACK_{hecho_id}_CUR_{cur_slug}.pdf")
        params = {
            "printBackground": True,
            "paperWidth": 8.27, "paperHeight": 11.69,
            "marginTop": 0.6, "marginBottom": 0.6, "marginLeft": 0.55, "marginRight": 0.55
        }
        pdf_b64 = safe_print_to_pdf(driver, params=params)
        with open(pdf_fallback, "wb") as f:      # <- fix del typo
            f.write(base64.b64decode(pdf_b64))
        return cur, pdf_fallback, True

    modal_html = clean_and_extract_modal_html(driver, modal_el)
    if not modal_html.strip():
        pdf_fallback = os.path.join(OUTPUT_PDF_DIR, f"Epicrisis_FALLBACK_{hecho_id}_CUR_{cur_slug}.pdf")
        params = {
            "printBackground": True,
            "paperWidth": 8.27, "paperHeight": 11.69,
            "marginTop": 0.6, "marginBottom": 0.6, "marginLeft": 0.55, "marginRight": 0.55
        }
        pdf_b64 = safe_print_to_pdf(driver, params=params)
        with open(pdf_fallback, "wb") as f:
            f.write(base64.b64decode(pdf_b64))
        return cur, pdf_fallback, True

    out_pdf = os.path.join(OUTPUT_PDF_DIR, f"Epicrisis_{hecho_id}_CUR_{cur_slug}.pdf")
    print_modal_to_pdf(driver, modal_html, out_pdf, cur, ORG_NAME)
    return cur, out_pdf, False

# ======================= MAIN =======================

if __name__ == "__main__":
    driver = build_driver()
    resultados = []
    try:
        iniciar_sesion(driver)  # setea ORG_NAME global

        start = time.time()
        for hid in range(START_HECHO_ID, END_HECHO_ID + 1):
            try:
                cur, pdf_path, fallback = procesar_hecho_epicrisis(driver, hid)
                resultados.append({
                    'NumeroHecho': hid,
                    'CUR': cur,
                    'Institucion': ORG_NAME,
                    'PDF': pdf_path,
                    'FallbackPaginaCompleta': fallback
                })
                pd.DataFrame(resultados).to_excel(OUTPUT_EXCEL, index=False)
                print(f"Hecho {hid} → CUR {cur or 'N/A'} → {os.path.basename(pdf_path)}")
            except Exception as e:
                print(f"[WARN] Hecho {hid} falló: {e}")
                resultados.append({'NumeroHecho': hid, 'CUR': 'Error', 'Institucion': ORG_NAME, 'PDF': '', 'FallbackPaginaCompleta': None})
                pd.DataFrame(resultados).to_excel(OUTPUT_EXCEL, index=False)

        elapsed = (time.time() - start) / 60
        print(f"Listo. PDFs en: {OUTPUT_PDF_DIR}. Duración: {elapsed:.2f} min.")

    finally:
        driver.quit()
