# Guion para video (máximo 2 minutos)

Preparación: tener Docker Desktop iniciado, terminal en el proyecto y navegador
abierto en http://localhost:8000. Ejecutar docker compose up --build -d antes de grabar.

- 0:00–0:10: «Este es el Analizador de representación de datos, creado con
  Python 3.12 y Django. Convierte números y analiza caracteres Unicode».
- 0:10–0:30: ingresar 2AF en base 16. Mostrar decimal 687, binario
  0000001010101111, octal 1257, hexadecimal 2AF, 10 bits significativos y 2 bytes.
- 0:30–0:45: ingresar 102 en base 2. Mostrar el mensaje de dígitos inválidos.
- 0:45–1:05: ingresar Año en el segundo formulario. Mostrar 3 caracteres y
  4 bytes. Explicar: «ñ es U+00F1; en UTF-8 usa los bytes C3 B1».
- 1:05–1:30: ejecutar docker compose exec -T web python manage.py test -v 2.
  Mostrar la cantidad real de pruebas y el resultado OK.
- 1:30–1:50: ejecutar docker compose ps y luego docker stats --no-stream
  con el ID del contenedor (ver README). Mostrar el límite de memoria de 256 MiB.
  La salida de inspect documenta además el límite de una CPU.
- 1:50–2:00: «El contenedor comparte el kernel del host Docker; cgroups limita
  sus recursos. El código y los comandos se encuentran en el README».

Subir el video y el proyecto a Google Drive o GitHub. Verificar que el docente
pueda abrir el enlace antes de entregar.
