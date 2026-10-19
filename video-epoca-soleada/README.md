# ANVA · Perfumes para época soleada (Reel / TikTok)

## Estado

**Reel editado:** `anva-epoca-soleada.mp4` (1080×1920, H.264, 30 fps, 40,6 s).

- **Cortes:** se quita el "Hola, ¿cómo están?" y se abre directamente con "Les voy a recomendar rápidamente…". Las pausas entre frases se acortan a unos 0,15 s y el encuadre alterna (100 % / 107 %) en cada corte para que los saltos no se noten.
- **Gancho:** "TEMPORADA DE CALOR · 2 PERFUMES ÁRABES", tomado de la primera frase.
- **Perfumes:**
  - Inserto N.º 1 Amber Oud Aqua Dubai cuando se nombra.
  - Comparación con Imagination de Louis Vuitton cuando se dice que lo "dupea".
  - Inserto N.º 2 Hawas Ice.
  - Cierre "¿Con cuál te quedas?" con los dos recomendados.
- **Subtítulos:** transcritos y corregidos. Arimo en blanco hueso; los nombres van en Josefin Sans Bold y los conceptos dichos (calor, fresco y jabonoso, dura bastante, fresco, dulzón) en champagne.
- **Audio:** voz limpia y normalizada a -14 LUFS. Base musical original (`tools/make_music.py`) unos 21 dB por debajo de la voz, con ducking.
- **Versión sin música:** existe una exportación solo con voz, para usar un audio con licencia de la biblioteca de Instagram o TikTok.

Para regenerarlo: `python3 tools/render_reel.py <crudo.mov> <fuentes> fotos <musica.wav> <salida>`. La transcripción se hizo con Whisper turbo y Parakeet v3 (sherpa-onnx, `tools/transcribe.py`).

## Perfumes identificados (según la etiqueta de cada foto)

| Foto | Casa | Nombre en pantalla |
|---|---|---|
| `fotos/hawas-ice.png` | Rasasi | HAWAS ICE |
| `fotos/imagination.png` | Louis Vuitton | IMAGINATION |
| `fotos/amber-oud-aqua-dubai.png` | Al Haramain | AMBER OUD AQUA DUBAI |

Solo se muestran la casa y el nombre. No se añadieron concentraciones, notas ni datos de rendimiento. Los frascos no se retocaron: las fotos ya venían con fondo transparente, así que solo se recortaron y se escalaron de forma proporcional.

## Recursos (`assets/`)

- `tarjeta-*.png`: 1080×1920, fondo #111111 con un halo de luz muy tenue en el tono de cada frasco (azul acero para Hawas Ice, verde agua para Imagination, azul celeste para Aqua Dubai), sombra de contacto y un reflejo corto. La casa va en Arimo champagne con interletrado amplio y el nombre en Josefin Sans Bold blanco hueso. Todo queda dentro de la zona segura: el texto termina antes de y=1520 y respeta 110 px de margen lateral.
- `inserto-*.mp4`: 3,2 s a 30 fps en H.264. El inserto entra con un fundido desde negro de 0,3 s, el frasco avanza un 3,5 % y el texto aparece a los 0,35 s subiendo 12 px. Se puede soltar directamente en la línea de tiempo.
- `tools/make_cards.py`: vuelve a generar las tarjetas y los insertos (`python3 make_cards.py <fuentes> fotos assets`). Las fuentes salen del repositorio oficial de Google Fonts.

## Guía de edición en CapCut (cuando tengas el video a mano)

1. **Proyecto:** 9:16, 1080×1920, con la frecuencia de fotogramas del original.
2. **Limpieza:** usa *Eliminar pausas* y revisa cada corte a mano. No cortes palabras ni respiraciones a mitad, y quita repeticiones y tomas falladas. Elimina la introducción hasta la primera frase con contenido.
3. **Gancho (0–3 s):** abre con la frase más fuerte que se diga sobre el calor o la frescura, siempre que se entienda sola. Si ninguna se sostiene fuera de contexto, empieza por la primera recomendación.
4. **Perfumes:** coloca `inserto-<perfume>.mp4` justo cuando se diga el nombre, cubriendo 2,5–3 s. La voz sigue sonando encima. Si en ese momento la persona está mostrando algo importante, usa la tarjeta PNG al 55 % de tamaño en el tercio inferior (posición Y ≈ -500) para no taparle la cara. Varía la presentación: inserto a pantalla completa en una recomendación y tarjeta reducida en otra.
5. **Subtítulos:** genera los automáticos en español y corrígelos sin cambiar el sentido.
   - Arimo, blanco hueso (#EFEBE3), 2 líneas como máximo, Y ≈ -420 y fuera de la franja derecha de botones.
   - Interletrado de 0,95.
   - Palabras clave en Josefin Sans Bold. El champagne (#C9B896) se reserva para una o dos palabras por recomendación, y solo si se dicen de verdad: calor, fresco, duración, carácter...
   - Sin animación palabra por palabra; basta un fundido de 0,15 s.
6. **Color:** contraste suave, negros profundos sin aplastarlos, saturación entre -5 y -10, temperatura +3 como mucho y piel natural.
7. **Audio:** *Reducir ruido* y *Normalizar volumen* sobre la voz, con la voz entre -14 y -16 LUFS. Música minimalista (deep house suave, lo-fi elegante o piano con pulso) de -24 a -28 dB por debajo de la voz, con ducking automático. Sin efectos de sonido, salvo un *whoosh* casi imperceptible al entrar un inserto.
8. **Cierre:** termina con la conclusión que la persona realmente dice. Solo si encaja con lo dicho, añade un texto breve: «¿Cuál elegirías tú?».
9. **Exportación:** MP4 H.264 a 1080p, con la frecuencia original y la tasa de bits en "Alta". Sin marca de agua ni marcos.

## Para terminar la edición completa aquí

Si se habilitan `drive.google.com` y `huggingface.co` en el acceso de red del entorno, o si el video se sube al repositorio, se puede automatizar todo: transcribir con faster-whisper, recortar silencios, sincronizar los insertos con la mención de cada perfume, quemar los subtítulos con las fuentes de la marca, mezclar la música y exportar el MP4 final.
