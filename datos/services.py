"""Operaciones puras de conversión y análisis Unicode."""
DIGITOS = {2: "01", 8: "01234567", 10: "0123456789", 16: "0123456789abcdefABCDEF"}


def convertir(numero, base):
    if base not in DIGITOS:
        raise ValueError("Seleccione una base válida: 2, 8, 10 o 16.")
    numero = numero.strip()
    if not numero:
        raise ValueError("Ingrese un número.")
    if numero.startswith("-"):
        raise ValueError("No se permiten valores negativos.")
    if any(c not in DIGITOS[base] for c in numero):
        raise ValueError(f"Dígitos inválidos para la base {base}.")
    # Se eliminan ceros iniciales antes de int: evita límites de conversión
    # con cadenas largas y permite detectar el rango sin enteros enormes.
    limpio = numero.lstrip("0") or "0"
    max_digitos = {2: 16, 8: 6, 10: 5, 16: 4}
    if len(limpio) > max_digitos[base]:
        raise ValueError("El valor debe estar entre 0 y 65535.")
    valor = int(limpio, base)
    if valor > 65535:
        raise ValueError("El valor debe estar entre 0 y 65535.")
    # Convención: cero se representa con un bit significativo y un byte.
    bits = max(1, valor.bit_length())
    cantidad_bytes = (bits + 7) // 8
    return {
        "decimal": valor,
        "binario": format(valor, f"0{cantidad_bytes * 8}b"),
        "octal": format(valor, "o"),
        "hexadecimal": format(valor, "X"),
        "bits": bits,
        "bytes": cantidad_bytes,
        "ancho": cantidad_bytes * 8,
    }


def analizar_texto(texto):
    if not texto:
        raise ValueError("Ingrese un texto.")
    if len(texto) > 20:
        raise ValueError("El texto debe tener como máximo 20 caracteres.")
    filas = []
    for caracter in texto:
        codigo = ord(caracter)
        try:
            datos = caracter.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError("El texto contiene un carácter Unicode no válido.") from exc
        filas.append({
            "caracter": caracter,
            "decimal": codigo,
            "punto": f"U+{codigo:04X}",
            "hexadecimal": hex(codigo),
            "utf8": " ".join(f"{byte:02X}" for byte in datos),
            "bytes": len(datos),
        })
    return {"filas": filas, "caracteres": len(texto), "bytes": len(texto.encode("utf-8"))}
