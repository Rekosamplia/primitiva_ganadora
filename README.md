# Sorteos Ganadores · Primitiva, Bonoloto y EuroDreams

Página web (un solo `index.html`, sin dependencias) que analiza **todo el histórico** de sorteos de
La Primitiva, Bonoloto y EuroDreams y genera combinaciones explicadas, dando más peso al último año.

## Qué hace

- **Selector de juego**: Primitiva (6/49), Bonoloto (6/49) y EuroDreams (6/40 + sueño).
- **Filtros de números**: más pesan (último año + histórico), más salidos, calientes del año,
  en racha (90 días), atrasados y fríos. Barra para ajustar el peso del último año.
- **Tablero interactivo**: 1 clic fija un número, 2 clics lo excluyen.
- **Generador** con 6 estrategias (ponderada, calientes, históricos, atrasados, mixta o según el filtro)
  que respeta los patrones reales del último año (suma, pares/impares, bajos/altos) y descarta
  combinaciones que ya han salido.
- **Explicación** de cada combinación: por qué se eligió cada número y cómo encaja con el histórico.
- Sugerencia de complementario y reintegro (Primitiva/Bonoloto) o sueño (EuroDreams).
- Gráfico de frecuencias, ranking y últimos sorteos. Modo claro/oscuro automático.

Se puede abrir un juego directamente con `index.html#primitiva`, `#bonoloto` o `#eurodreams`.

## Estructura

```
index.html                      ← la web generada (datos incluidos dentro)
datos/*.json                    ← histórico normalizado de cada juego
scripts/plantilla.html          ← código fuente de la web (editar aquí)
scripts/actualizar.py           ← descarga datos nuevos y genera index.html
.github/workflows/actualizar.yml← actualización automática diaria
```

Formato de cada sorteo en `datos/*.json`:
`["AAAA-MM-DD", [n1..n6], complementario | sueño, reintegro]`

## Publicar en GitHub Pages

1. Crea un repositorio y sube esta carpeta.
2. En **Settings → Pages**, elige *Deploy from a branch*, rama `main` y carpeta `/ (root)`.
3. En **Settings → Actions → General → Workflow permissions**, marca *Read and write permissions*
   para que la actualización diaria pueda guardar los sorteos nuevos.
4. La web quedará en `https://<tu-usuario>.github.io/<repositorio>/`.

## Actualizar los datos

Automático: la Action **Actualizar sorteos** se ejecuta cada día a las 07:00 UTC; si hay sorteos
nuevos, guarda `datos/` e `index.html` y GitHub Pages se republica solo. También se puede lanzar a
mano desde la pestaña *Actions → Actualizar sorteos → Run workflow*.

En local (Python 3.8+, sin instalar nada):

```bash
python3 scripts/actualizar.py                 # descarga y reconstruye
python3 scripts/actualizar.py --sin-descarga  # solo reconstruye tras editar la plantilla
```

Si la descarga falla o trae menos sorteos de los que ya hay, el script conserva los datos actuales.

## Fuente de datos

Hojas públicas de [lotoideas.com](https://www.lotoideas.com/), que recopilan los resultados oficiales
de Loterías y Apuestas del Estado. Primitiva desde 1985, Bonoloto desde 1988 y EuroDreams desde 2023.

## Aviso

Cada sorteo es independiente y todas las combinaciones tienen la misma probabilidad
(1 entre 13.983.816 en Primitiva/Bonoloto; 1 entre 19.191.900 en EuroDreams con sueño).
Las estadísticas pasadas no predicen resultados futuros: esto es un juego para elegir con criterio,
no un método para ganar. Juega con responsabilidad.
