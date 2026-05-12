import flet as ft

candidates = [
    {'primary':'#111','secondary':'#222','background':'#f'},
    {'primary':'#111','secondary':'#222','background_color':'#f'},
    {'primary':'#111','secondary':'#222','surface':'#f'},
    {'primary':'#111','secondary':'#222','surface_color':'#f'},
    {'primary':'#111','secondary':'#222','background':'#f','surface':'#fff'},
]

for kw in candidates:
    try:
        cs = ft.ColorScheme(**kw)
        print('OK for', list(kw.keys()))
    except Exception as e:
        print('ERR for', list(kw.keys()), '->', type(e).__name__, e)

print('attrs:', [a for a in dir(ft.ColorScheme) if not a.startswith('_')][:50])
