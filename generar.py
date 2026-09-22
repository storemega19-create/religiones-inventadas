
#!/usr/bin/env python3
"""
Generador diario de "religión inventada" para Instagram Historias.
Uso:
    python3 generar.py                       -> tema aleatorio
    python3 generar.py "un tema concreto"    -> ese tema
"""
import os, sys, json, random, re, unicodedata, datetime, urllib.request, platform
from PIL import Image, ImageDraw, ImageFont

# Detectar SO y rutas de fuentes
if platform.system() == "Windows":
    FONT_DIR = "C:\\Windows\\Fonts\\"
    serifB = FONT_DIR + "georgiab.ttf"
    serif = FONT_DIR + "georgia.ttf"
    serifI = FONT_DIR + "georgiai.ttf"
    sans = FONT_DIR + "arial.ttf"
    sansB = FONT_DIR + "arialbd.ttf"
else:
    FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
    serifB = FONT_DIR + "DejaVuSerif-Bold.ttf"
    serif = FONT_DIR + "DejaVuSerif.ttf"
    serifI = FONT_DIR + "DejaVuSerif-Italic.ttf"
    sans = FONT_DIR + "DejaVuSans.ttf"
    sansB = FONT_DIR + "DejaVuSans-Bold.ttf"

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salidas")
W, H = 1080, 2200

PALETAS = [
    ((23, 26, 18),   (233, 226, 204), (240, 138, 36),  (58, 63, 46)),
    ((13, 22, 51),   (239, 232, 214), (212, 172, 82),  (42, 55, 102)),
    ((59, 15, 30),   (245, 232, 214), (227, 176, 75),  (102, 44, 60)),
    ((236, 242, 244),(15, 42, 58),    (13, 122, 126),  (196, 210, 216)),
    ((240, 207, 92), (26, 26, 26),   (92, 76, 20),    (200, 170, 64)),
    ((26, 28, 33),   (230, 230, 225),(150, 190, 160), (55, 58, 64)),
    ((250, 240, 222),(40, 30, 20),   (168, 56, 43),   (214, 198, 168)),
]

TEMAS_RESERVA = [
    "una religión que adora las notificaciones sin leer",
    "un culto que espera que el capítulo se cargue en la plataforma de streaming",
    "una secta que reza a la batería al 1% que nunca se apaga",
    "una fe que cree que el número perdido siempre acaba llamando",
    "una religión que venera el carrito de la compra abandonado, nunca comprado",
    "un culto a la reunión que podría haber sido un email",
    "una religión que adora el archivo guardado como 'definitivo_final_v2'",
    "una fe basada en el three-way call que nunca se contesta a tiempo",
]

SYSTEM_PROMPT = """Eres un escritor satírico en español de España, ingenioso y breve.
Inventas religiones absurdas y cortas para una serie de imágenes de Instagram.
El humor va sobre estructuras y comportamientos humanos.
Responde EXCLUSIVAMENTE en JSON válido, sin texto antes ni después."""

def llamar_api(system_prompt, user_msg, api_key):
    body = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 2000,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_msg}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        return "".join(b["text"] for b in data["content"] if b.get("type") == "text")
    except urllib.error.HTTPError as e:
        print(f"ERROR API HTTP {e.code}: {e.reason}")
        print(f"Respuesta: {e.read().decode()}")
        raise
    except Exception as e:
        print(f"ERROR API: {e}")
        raise

def pedir_contenido(tema):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Aviso: sin ANTHROPIC_API_KEY, se usa el generador local (gratis).")
        return generar_local(tema)
    if not tema:
        tema = random.choice(TEMAS_RESERVA)
    
    # Generar 4 lotes de 5 candidatas
    todas_candidatas = []
    for lote in range(1, 5):
        user_msg = f"""Genera 5 ideas cortas sobre: {tema}
Perspectiva {lote}/4. Ángulos completamente distintos a los anteriores.

JSON en UNA LÍNEA (sin saltos):
[{{"nombre":"X","eslogan":"y","detalle":"z","puntos":["a","b"],"mandamiento":"c","pie_imagen":"d","libro_sagrado":""}}...]"""
        
        try:
            text = llamar_api(SYSTEM_PROMPT, user_msg, api_key)
            text = re.sub(r'\n|\r', ' ', text.strip())
            text = re.sub(r"^```json\s*|\s*```$", "", text.strip())
            candidatas_lote = json.loads(text)
            todas_candidatas.extend(candidatas_lote)
        except (json.JSONDecodeError, urllib.error.HTTPError, Exception):
            pass
    
    if not todas_candidatas:
        return generar_local(tema)
    
    # Seleccionar la mejor de todas
    lista_json = json.dumps(todas_candidatas[:20], ensure_ascii=False)
    user_msg_seleccion = f"""Elige la MEJOR de estas religiones (más ingeniosa: gracia + profundidad).

JSON UNA LÍNEA:
{{"ganadora":{{"nombre":"...","eslogan":"...","detalle":"...","puntos":["...","..."],"mandamiento":"...","pie_imagen":"...","libro_sagrado":""}}}}

Candidatas: {lista_json}"""
    
    try:
        text_seleccion = llamar_api(SYSTEM_PROMPT, user_msg_seleccion, api_key)
        text_seleccion = re.sub(r'\n|\r', ' ', text_seleccion.strip())
        text_seleccion = re.sub(r"^```json\s*|\s*```$", "", text_seleccion.strip())
        resultado = json.loads(text_seleccion)
        return resultado["ganadora"]
    except (json.JSONDecodeError, urllib.error.HTTPError, Exception):
        return random.choice(todas_candidatas)

def generar_local(tema):
    NUCLEOS = [
        ("Cargador Perdido", "Nunca está donde lo dejaste.",
         ["El cable bueno se esconde solo.", "Encontrarlo es un acto de fe."],
         "No comprarás un cargador nuevo sin buscar antes 10 minutos."),
        ("Capítulo Siguiente", "Ya casi carga.",
         ["La ruedecita gira por ti.", "Saltarse el intro es pecado venial."],
         "No cerrarás la app antes del final."),
        ("Wifi del Vecino", "Casi tiene contraseña.",
         ["Una barra basta para creer.", "El router ajeno también escucha tus plegarias."],
         "No preguntarás la clave dos veces."),
        ("Carrito Abandonado", "Lo compras mañana.",
         ["27 artículos, cero prisa.", "El descuento expira, la fe no."],
         "No vaciarás el carrito sin pensarlo tres días."),
        ("Grupo de WhatsApp", "Alguien está escribiendo…",
         ["El doble check azul tarda lo que tenga que tardar.", "Silenciar no es abandonar."],
         "No preguntarás '¿lo has visto?' antes de una hora."),
    ]
    nucleo, eslogan, puntos, mandamiento = random.choice(NUCLEOS)
    prefijo = random.choice(["La Iglesia del", "La Orden del", "El Culto al", "La Secta de la"])
    nombre = f"{prefijo} {nucleo}"
    return {
        "nombre": nombre,
        "eslogan": eslogan,
        "detalle": tema if tema else "Nueva fe, sin dinero real.",
        "puntos": puntos,
        "mandamiento": mandamiento,
        "pie_imagen": random.choice(["Sin dinero real.", "Sin dinero real. Solo fe."]),
        "libro_sagrado": "",
    }

def wrap_fit(draw, text, font_path, max_w, start_size, min_size=16):
    size = start_size
    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        
        # Intenta dividir en líneas
        palabras = text.split(" ")
        lineas_prueba = []
        linea_actual = ""
        
        for palabra in palabras:
            prueba = (linea_actual + " " + palabra).strip()
            bbox = draw.textbbox((0, 0), prueba, font=font)
            
            if bbox[2] - bbox[0] > max_w:
                # No cabe con la palabra actual
                if linea_actual:
                    lineas_prueba.append(linea_actual)
                    linea_actual = ""
                
                # Ahora intenta meter solo la palabra
                bbox_palabra = draw.textbbox((0, 0), palabra, font=font)
                if bbox_palabra[2] - bbox_palabra[0] <= max_w:
                    # La palabra cabe sola
                    linea_actual = palabra
                else:
                    # La palabra es demasiado larga, romper por caracteres
                    for i, char in enumerate(palabra):
                        prueba_char = linea_actual + char
                        bbox_char = draw.textbbox((0, 0), prueba_char, font=font)
                        if bbox_char[2] - bbox_char[0] > max_w:
                            if linea_actual:
                                lineas_prueba.append(linea_actual)
                            linea_actual = char
                        else:
                            linea_actual = prueba_char
            else:
                linea_actual = prueba
        
        if linea_actual:
            lineas_prueba.append(linea_actual)
        
        # Verifica que TODAS las líneas caben
        todas_caben = True
        for linea in lineas_prueba:
            bbox = draw.textbbox((0, 0), linea, font=font)
            if bbox[2] - bbox[0] > max_w:
                todas_caben = False
                break
        
        if todas_caben:
            return font
        size -= 2
    return ImageFont.truetype(font_path, min_size)

def dibujar(contenido, paleta):
    bg, ink, accent, line = paleta
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    M = 80

    d.text((M, 150), "Sin dinero real", font=ImageFont.truetype(sans, 26), fill=accent)

    nombre = contenido["nombre"]
    palabras = nombre.split(" ")
    f_nombre = wrap_fit(d, nombre, serifB, W - 2*M, 80)
    y = 220
    linea = ""
    lineas = []
    for w_ in palabras:
        prueba = (linea + " " + w_).strip()
        bbox = d.textbbox((0, 0), prueba, font=f_nombre)
        if bbox[2] - bbox[0] > W - 2*M and linea:
            lineas.append(linea)
            linea = w_
        else:
            linea = prueba
    if linea:
        lineas.append(linea)
    for l in lineas[:3]:
        d.text((M, y), l, font=f_nombre, fill=ink)
        y += int(f_nombre.size * 1.1)

    y += 120
    f_eslogan = wrap_fit(d, contenido["eslogan"], serifB, W - 2*M, 100)
    palabras = contenido["eslogan"].split(" ")
    linea = ""
    lineas = []
    for w_ in palabras:
        prueba = (linea + " " + w_).strip()
        bbox = d.textbbox((0, 0), prueba, font=f_eslogan)
        if bbox[2] - bbox[0] > W - 2*M and linea:
            lineas.append(linea)
            linea = w_
        else:
            linea = prueba
    if linea:
        lineas.append(linea)
    for l in lineas[:4]:
        d.text((M, y), l, font=f_eslogan, fill=accent)
        y += int(f_eslogan.size * 1.1)

    y += 100
    detalle = contenido.get("detalle", "")
    f_detalle = wrap_fit(d, detalle, sans, W - 2*M, 28)
    palabras_det = detalle.split(" ")
    linea = ""
    lineas = []
    for w_ in palabras_det:
        prueba = (linea + " " + w_).strip()
        bbox = d.textbbox((0, 0), prueba, font=f_detalle)
        if bbox[2] - bbox[0] > W - 2*M and linea:
            lineas.append(linea)
            linea = w_
        else:
            linea = prueba
    if linea:
        lineas.append(linea)
    for l in lineas:
        d.text((M, y), l, font=f_detalle, fill=ink)
        y += int(f_detalle.size * 1.2)
    y += 40

    d.line([M, y, W - M, y], fill=line, width=2)
    y += 80
    for p in contenido.get("puntos", [])[:3]:
        f_p = wrap_fit(d, p, sans, W - 2*M, 28)
        palabras_p = p.split(" ")
        linea = ""
        lineas = []
        for w_ in palabras_p:
            prueba = (linea + " " + w_).strip()
            bbox = d.textbbox((0, 0), prueba, font=f_p)
            if bbox[2] - bbox[0] > W - 2*M and linea:
                lineas.append(linea)
                linea = w_
            else:
                linea = prueba
        if linea:
            lineas.append(linea)
        for l in lineas:
            d.text((M, y), l, font=f_p, fill=ink)
            y += int(f_p.size * 1.2)
        y += 40

    y += 80
    d.text((M, y), "Mandamiento único:", font=ImageFont.truetype(serifI, 36), fill=accent)
    y += 65
    mandamiento = contenido["mandamiento"]
    f_mand = wrap_fit(d, mandamiento, serifB, W - 2*M, 44)
    palabras_mand = mandamiento.split(" ")
    linea = ""
    lineas = []
    for w_ in palabras_mand:
        prueba = (linea + " " + w_).strip()
        bbox = d.textbbox((0, 0), prueba, font=f_mand)
        if bbox[2] - bbox[0] > W - 2*M and linea:
            lineas.append(linea)
            linea = w_
        else:
            linea = prueba
    if linea:
        lineas.append(linea)
    for l in lineas:
        d.text((M, y), l, font=f_mand, fill=ink)
        y += int(f_mand.size * 1.2)
    y += 40

    if contenido.get("libro_sagrado"):
        d.text((M, y), f"Libro sagrado: {contenido['libro_sagrado']}", font=ImageFont.truetype(serifI, 26), fill=ink)

    d.text((M, H - 80), contenido.get("pie_imagen", "Sin dinero real."), font=ImageFont.truetype(sans, 24), fill=accent)
    return img

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:40] or "religion"

def enviar_telegram(imagen_path):
    """Envía la imagen a Telegram"""
    print(f"DEBUG: Checking if {imagen_path} exists...")
    if not os.path.exists(imagen_path):
        print(f"❌ ERROR: Archivo no encontrado: {imagen_path}")
        return
    
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    print(f"DEBUG: bot_token={'*' * 10 if bot_token else 'NONE'}, chat_id={chat_id}")
    
    if not bot_token or not chat_id:
        print("❌ Sin credenciales Telegram")
        return
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        with open(imagen_path, 'rb') as img_file:
            img_data = img_file.read()
        print(f"DEBUG: Image size: {len(img_data)} bytes")
        
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body = f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="religion.png"\r\nContent-Type: image/png\r\n\r\n'.encode()
        body += img_data
        body += f'\r\n--{boundary}--\r\n'.encode()
        
        print(f"DEBUG: Enviando a Telegram...")
        req = urllib.request.Request(url, data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            print(f"✓ Telegram OK: {result.get('ok')}")
    except urllib.error.HTTPError as e:
        print(f"❌ Error Telegram HTTP {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

def main():
    tema = " ".join(sys.argv[1:]).strip() or None
    contenido = pedir_contenido(tema)
    paleta = random.choice(PALETAS)
    img = dibujar(contenido, paleta)

    os.makedirs(OUT_DIR, exist_ok=True)
    fecha = datetime.date.today().isoformat()
    slug = slugify(contenido["nombre"])
    path = os.path.join(OUT_DIR, f"{fecha}-{slug}.png")
    img.save(path)
    print(json.dumps({"path": path, "contenido": contenido}, ensure_ascii=False, indent=2), flush=True)
    
    # Enviar a Telegram
    enviar_telegram(path)

if __name__ == "__main__":
    main()
