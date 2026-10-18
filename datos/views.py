from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .forms import NumeroForm, TextoForm


@require_http_methods(["GET", "POST"])
def inicio(request):
    numero_form = NumeroForm()
    texto_form = TextoForm()
    numero_resultado = texto_resultado = None
    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "numero":
            numero_form = NumeroForm(request.POST)
            if numero_form.is_valid():
                numero_resultado = numero_form.resultado
        elif accion == "texto":
            texto_form = TextoForm(request.POST)
            if texto_form.is_valid():
                texto_resultado = texto_form.resultado
        else:
            numero_form = NumeroForm(request.POST)
            numero_form.is_valid()
            numero_form.add_error(None, "Seleccione un formulario válido.")
    return render(request, "datos/inicio.html", {
        "numero_form": numero_form, "texto_form": texto_form,
        "numero": numero_resultado, "texto": texto_resultado,
    })
