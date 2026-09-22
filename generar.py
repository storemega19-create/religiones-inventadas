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
        "https:/
