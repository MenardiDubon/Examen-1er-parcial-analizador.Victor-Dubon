# Analizador de representación de datos
#### Video demostrativo

[▶ Ver video de la aplicación funcionando en Docker](https://drive.google.com/file/d/1LBF99VX34-cWThFgVjx0JLfURfmTmWJ7/view?usp=sharing)

Aplicación académica en Python 3.12 y Django 5.2. Dos formularios independientes
convierten enteros entre bases y muestran los puntos de código Unicode y bytes
UTF-8 de cada carácter. No requiere base de datos, migraciones ni servicios externos.

## Ejecutar localmente (Windows)

Abrir PowerShell o CMD dentro de la carpeta que contiene manage.py:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python manage.py check
.venv\Scripts\python manage.py test -v 2
.venv\Scripts\python manage.py runserver
```

En Git Bash, los comandos equivalentes son:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python manage.py test -v 2
.venv/Scripts/python manage.py runserver
```

Linux/macOS: crear el entorno con `python3.12 -m venv .venv` y usar
`.venv/bin/python` en los siguientes comandos.

Abrir http://localhost:8000. Detener el servidor con Ctrl+C. El servidor muestra
la dirección local; para acceso desde otros equipos se necesita configurar la
interfaz de escucha, ALLOWED_HOSTS y la red del equipo.

## Docker y Compose

Instalar e iniciar Docker Desktop con contenedores Linux (o Docker Engine y el
plugin Compose en Linux). Desde la carpeta del proyecto:

```bash
docker compose config
docker compose up --build -d
docker compose ps
docker compose exec -T web python manage.py check
docker compose exec -T web python manage.py test -v 2
docker compose logs web
```

Abrir http://localhost:8000. `Dockerfile` usa `python:3.12-slim`, publica el puerto
8000 y ejecuta la aplicación con un usuario sin privilegios. `compose.yaml` aplica
`mem_limit: 256m`, `memswap_limit: 256m` (sin swap adicional) y `cpus: 1.0`.
Es una demostración académica: `runserver` no es un servidor de producción.

Para detener y eliminar el contenedor:

```bash
docker compose down
```

### Obtener evidencia real de recursos

En PowerShell:

```powershell
$idContenedor = docker compose ps -q web
docker stats --no-stream $idContenedor | Tee-Object -FilePath evidencias/docker-stats.txt
docker inspect --format '{{.HostConfig.Memory}} {{.HostConfig.NanoCpus}}' $idContenedor
docker compose exec -T web python manage.py test -v 2 2>&1 | Tee-Object -FilePath evidencias/pruebas-docker.txt
```

En Git Bash/Linux/macOS:

```bash
contenedor_id=$(docker compose ps -q web)
docker stats --no-stream "$contenedor_id" | tee evidencias/docker-stats.txt
docker inspect --format '{{.HostConfig.Memory}} {{.HostConfig.NanoCpus}}' "$contenedor_id"
docker compose exec -T web python manage.py test -v 2 2>&1 | tee evidencias/pruebas-docker.txt
```

`docker stats` debe mostrar un límite de **256 MiB**. El consumo observado depende
de la ejecución y no se debe inventar. `inspect` debe devolver **268435456** bytes
de memoria y **1000000000** NanoCpus (una CPU). Una CPU es una cuota equivalente
a un núcleo, no necesariamente afinidad a un núcleo concreto.

Tomar una captura de la salida real y guardar el video de máximo dos minutos.
Ver GUION_VIDEO.md. Docker no está disponible en el entorno de preparación:
la ejecución del contenedor, sus estadísticas y el video quedan pendientes.

## Uso y resultados esperados

| Entrada | Base | Decimal | Binario ajustado | Octal | Hex | Bits significativos | Bytes |
|---|---:|---:|---|---|---|---:|---:|
| 2AF | 16 | 687 | 0000001010101111 | 1257 | 2AF | 10 | 2 |
| 255 | 10 | 255 | 11111111 | 377 | FF | 8 | 1 |
| 256 | 10 | 256 | 0000000100000000 | 400 | 100 | 9 | 2 |
| 0 | 10 | 0 | 00000000 | 0 | 0 | 1 | 1 |
| FFFF | 16 | 65535 | 1111111111111111 | 177777 | FFFF | 16 | 2 |

Se aceptan dígitos ASCII de la base elegida, con A–F en mayúscula o minúscula.
No se aceptan signos +/−, prefijos 0b/0o/0x, separadores ni decimales. Se recortan
espacios exteriores del número. Hay mensajes específicos para entradas vacías,
valores negativos, dígitos inválidos, base inválida y valores mayores de 65535.
El campo numérico acepta hasta 256 dígitos como protección de entrada.

### Ajuste a bytes

Para n > 0: bits significativos = `n.bit_length()`; bytes = `(bits + 7) // 8`;
ancho = `bytes * 8`. El formato binario rellena con ceros a ese ancho.
Para cero se adopta explícitamente 1 bit significativo y 1 byte (Python devuelve
0 en `0.bit_length()`). El rango solicitado utiliza como máximo 16 bits;
la fórmula también produce anchos de 24, 32… para rangos mayores.

### Texto y Unicode

Se admiten de 1 a 20 puntos de código Python, incluidos espacios, que se preservan.
Un grafema visual puede contener varios puntos de código, por ejemplo una letra
con un acento combinante. No se normaliza ni modifica el texto recibido.

Para «Año» se muestran 3 caracteres y 4 bytes:

| Carácter | Decimal | Punto de código | Hexadecimal | Bytes UTF-8 |
|---|---:|---|---|---|
| A | 65 | U+0041 | 0x41 | 41 |
| ñ | 241 | U+00F1 | 0xf1 | C3 B1 |
| o | 111 | U+006F | 0x6f | 6F |

`ord()` devuelve el punto de código; `.encode('utf-8')` devuelve los bytes.
El código Unicode de ñ (F1) no es la secuencia de bytes UTF-8 (C3 B1).
Las plantillas escapan HTML y los formularios POST incluyen protección CSRF.

## Estructura

- `config/settings.py`: configuración de Django, aplicaciones, plantillas y middleware.
- `config/urls.py`: relaciona la ruta `/` con la vista.
- `datos/views.py`: recibe GET/POST, valida y entrega el contexto a la plantilla.
- `datos/forms.py`: formularios, límites y mensajes.
- `datos/services.py`: conversión y análisis Unicode.
- `datos/templates/datos/inicio.html`: interfaz adaptable con ambos formularios.
- `datos/tests.py`: 16 pruebas, además de casos múltiples mediante subTest.
- `Dockerfile`, `compose.yaml`: contenedor, puerto y límites.

## Pruebas automatizadas

```bash
python manage.py test -v 2
```

Se cubren las cuatro bases, límites 0/255/256/65535, relleno binario, dígitos y
bases inválidos, valores negativos y fuera de rango, entrada vacía, hexadecimal
en minúscula, longitud del texto, ñ en UTF-8, espacios, emoji, integración de
formularios y vistas, escape HTML, CSRF y acciones inválidas. Las pruebas son
SimpleTestCase: no crean ni usan base de datos.

## Arquitectura de Von Neumann

La CPU ejecuta el intérprete Python y el código de Django. La unidad de control
coordina la búsqueda, decodificación y ejecución de instrucciones; la ALU realiza
operaciones aritméticas y lógicas usadas al convertir y validar. Registros y
cachés mantienen datos temporales. La RAM almacena instrucciones y datos durante
la ejecución (cadenas, enteros, objetos y respuestas HTML). El almacenamiento
conserva código e imagen Docker; teclado, navegador y red proporcionan entrada y
salida. Los buses e interconexiones transportan direcciones, datos y señales de
control entre CPU, memoria y dispositivos. La aplicación usa estos recursos a
través del sistema operativo; no manipula directamente MAR, MBR o el bus físico.

Un contenedor agrupa procesos aislados con namespaces y limita recursos mediante
cgroups. No incluye un kernel propio como una máquina virtual: usa el kernel del
host Docker. En Docker Desktop para Windows/macOS, los contenedores Linux usan el
kernel Linux de la máquina virtual que ejecuta Docker, no directamente el kernel
de Windows/macOS. La imagen aporta Python, sus bibliotecas y el espacio de usuario.

La aplicación no guarda información: cada análisis existe solo durante la petición.
Por eso no requiere volumen. Si se incorporara una base de datos o archivos
persistentes, sus datos deberían almacenarse en un volumen independiente del
contenedor, con copias de seguridad según el uso.

## Entrega

1. Ejecutar el contenedor y las pruebas; guardar estadísticas y capturas reales.
2. Grabar el video siguiendo GUION_VIDEO.md, sin superar 2 minutos.
3. Cargar el proyecto y el video en GitHub o Google Drive desde la cuenta del autor.
4. Configurar el acceso del docente y comprobar el enlace antes de entregarlo.

No se ha creado un enlace externo de GitHub/Drive ni un video en esta preparación.
