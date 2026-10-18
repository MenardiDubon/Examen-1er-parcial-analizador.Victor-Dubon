from django.test import SimpleTestCase, Client
from .services import convertir, analizar_texto
from .forms import NumeroForm, TextoForm


class ConversionTests(SimpleTestCase):
    def test_bases_validas(self):
        for numero, base in [("1010101111", 2), ("1257", 8), ("687", 10), ("2AF", 16)]:
            with self.subTest(base=base):
                r = convertir(numero, base)
                self.assertEqual(r["decimal"], 687)
                self.assertEqual(r["binario"], "0000001010101111")
                self.assertEqual((r["octal"], r["hexadecimal"]), ("1257", "2AF"))
                self.assertEqual((r["bits"], r["bytes"]), (10, 2))

    def test_limites_de_byte(self):
        for valor, bits, cantidad, ancho in [(0, 1, 1, 8), (1, 1, 1, 8), (255, 8, 1, 8), (256, 9, 2, 16), (65535, 16, 2, 16)]:
            with self.subTest(valor=valor):
                r = convertir(str(valor), 10)
                self.assertEqual((r["bits"], r["bytes"], len(r["binario"])), (bits, cantidad, ancho))
                self.assertEqual(int(r["binario"], 2), valor)

    def test_digitos_invalidos(self):
        for numero, base in [("102", 2), ("8", 8), ("A", 10), ("G", 16), ("0xFF", 16), ("+5", 10), ("1_0", 10), ("١", 10)]:
            with self.subTest(numero=numero, base=base):
                with self.assertRaisesRegex(ValueError, "Dígitos inválidos"):
                    convertir(numero, base)

    def test_base_invalida(self):
        with self.assertRaisesRegex(ValueError, "base válida"):
            convertir("10", 3)
        self.assertFalse(NumeroForm({"numero": "10", "base": "3"}).is_valid())

    def test_fuera_de_rango(self):
        for numero, base in [("65536", 10), ("10000", 16), ("200000", 8), ("1" + "0" * 16, 2)]:
            with self.subTest(base=base):
                with self.assertRaisesRegex(ValueError, "entre 0 y 65535"):
                    convertir(numero, base)

    def test_negativos(self):
        with self.assertRaisesRegex(ValueError, "negativos"):
            convertir("-1", 10)

    def test_entrada_vacia(self):
        with self.assertRaisesRegex(ValueError, "Ingrese un número"):
            convertir("  ", 10)
        self.assertFalse(NumeroForm({"numero": "", "base": "10"}).is_valid())

    def test_hex_minusculas_y_ceros(self):
        self.assertEqual(convertir("00af", 16)["decimal"], 175)
        self.assertEqual(convertir("0" * 200 + "1", 10)["decimal"], 1)


class TextoTests(SimpleTestCase):
    def test_ano_utf8(self):
        r = analizar_texto("Año")
        self.assertEqual((r["caracteres"], r["bytes"]), (3, 4))
        self.assertEqual(r["filas"][1], {"caracter": "ñ", "decimal": 241,
            "punto": "U+00F1", "hexadecimal": "0xf1", "utf8": "C3 B1", "bytes": 2})

    def test_maximo_y_vacio(self):
        self.assertTrue(TextoForm({"texto": "a" * 20}).is_valid())
        self.assertFalse(TextoForm({"texto": "a" * 21}).is_valid())
        self.assertFalse(TextoForm({"texto": ""}).is_valid())
        for texto in ("", "a" * 21):
            with self.subTest(texto=texto):
                with self.assertRaises(ValueError):
                    analizar_texto(texto)

    def test_espacios_y_emoji(self):
        r = analizar_texto(" 😀 ")
        self.assertEqual((r["caracteres"], r["bytes"]), (3, 6))
        self.assertEqual(r["filas"][1]["utf8"], "F0 9F 98 80")


class VistaTests(SimpleTestCase):
    def test_get_y_conversion(self):
        self.assertContains(self.client.get("/"), "Analizador de representación")
        r = self.client.post("/", {"accion": "numero", "numero": "2AF", "base": "16"})
        self.assertContains(r, "0000001010101111")
        self.assertEqual(r.context["numero"]["decimal"], 687)

    def test_error_sin_resultado(self):
        r = self.client.post("/", {"accion": "numero", "numero": "102", "base": "2"})
        self.assertContains(r, "Dígitos inválidos")
        self.assertIsNone(r.context["numero"])

    def test_texto_escapado_y_utf8(self):
        r = self.client.post("/", {"accion": "texto", "texto": "Año"})
        self.assertContains(r, "C3 B1")
        self.assertEqual(r.context["texto"]["bytes"], 4)
        r = self.client.post("/", {"accion": "texto", "texto": "<script>"})
        self.assertNotContains(r, "<script>")

    def test_csrf(self):
        cliente = Client(enforce_csrf_checks=True)
        self.assertEqual(cliente.post("/", {"accion": "texto", "texto": "Año"}).status_code, 403)
        cliente.get("/")
        token = cliente.cookies["csrftoken"].value
        self.assertEqual(cliente.post("/", {"accion": "texto", "texto": "Año", "csrfmiddlewaretoken": token}).status_code, 200)

    def test_accion_invalida(self):
        self.assertContains(self.client.post("/", {"accion": "otra"}), "formulario válido")
