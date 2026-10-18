from django import forms
from .services import convertir, analizar_texto


class NumeroForm(forms.Form):
    numero = forms.CharField(label="Número", max_length=256,
        error_messages={"required": "Ingrese un número.", "max_length": "Ingrese como máximo 256 dígitos."},
        widget=forms.TextInput(attrs={"placeholder": "Ejemplo: 2AF", "autocomplete": "off"}))
    base = forms.TypedChoiceField(label="Base de origen", coerce=int, choices=[
        (2, "2 · Binario"), (8, "8 · Octal"), (10, "10 · Decimal"), (16, "16 · Hexadecimal")],
        initial=10, error_messages={"required": "Seleccione una base.", "invalid_choice": "Seleccione una base válida: 2, 8, 10 o 16."})

    def clean(self):
        datos = super().clean()
        if "numero" in datos and "base" in datos:
            try:
                self.resultado = convertir(datos["numero"], datos["base"])
            except ValueError as exc:
                self.add_error("numero", str(exc))
        return datos


class TextoForm(forms.Form):
    texto = forms.CharField(label="Texto (máximo 20 caracteres)", max_length=20, strip=False,
        error_messages={"required": "Ingrese un texto.", "max_length": "El texto debe tener como máximo 20 caracteres."},
        widget=forms.TextInput(attrs={"placeholder": "Ejemplo: Año"}))

    def clean_texto(self):
        texto = self.cleaned_data["texto"]
        try:
            self.resultado = analizar_texto(texto)
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        return texto
