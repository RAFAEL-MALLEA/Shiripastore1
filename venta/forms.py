from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Plataforma, Categoria, Coleccion, Inventario, MensajeContacto


class PlataformaForm(forms.ModelForm):
    class Meta:
        model = Plataforma
        fields = ["plataforma"]
        labels = {"plataforma": "Plataforma"}
        widgets = {"plataforma": forms.TextInput(attrs={"class": "form-control"})}


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["categoria"]
        labels = {"categoria": "Categoría"}
        widgets = {"categoria": forms.TextInput(attrs={"class": "form-control"})}


class ColeccionForm(forms.ModelForm):
    class Meta:
        model = Coleccion
        fields = ["coleccion"]
        labels = {"coleccion": "Colección"}
        widgets = {"coleccion": forms.TextInput(attrs={"class": "form-control"})}


class InventarioForm(forms.ModelForm):
    """Reemplaza el manejo manual de request.POST[...] en views.py,
    que no validaba nada y repetía mucho código."""
    class Meta:
        model = Inventario
        fields = [
            "Id_categoria", "Id_plataforma", "Id_coleccion",
            "nombre_juego", "valor", "stock", "disponible", "imagen",
        ]
        widgets = {
            "Id_categoria": forms.Select(attrs={"class": "form-select"}),
            "Id_plataforma": forms.Select(attrs={"class": "form-select"}),
            "Id_coleccion": forms.Select(attrs={"class": "form-select"}),
            "nombre_juego": forms.TextInput(attrs={"class": "form-control"}),
            "valor": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "disponible": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "imagen": forms.TextInput(attrs={"class": "form-control"}),
        }


class RegistroForm(UserCreationForm):
    """Registro real de clientes usando el sistema de usuarios de Django
    (auth_user), en vez del modelo 'Usuarios' que nunca se usaba.
    """
    first_name = forms.CharField(
        label="Nombre", max_length=40, required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="Apellidos", max_length=50, required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        label="Correo", required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    class Meta:
        # NOTA: password1/password2 NO van aquí. No son campos reales del
        # modelo User (son campos declarados aparte, heredados de
        # UserCreationForm); incluirlos en Meta.fields de un ModelForm
        # lanza FieldError porque Django los busca en el modelo.
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta registrada con ese correo.")
        return email


class MensajeContactoForm(forms.ModelForm):
    class Meta:
        model = MensajeContacto
        fields = ["email", "motivo", "mensaje"]
        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "form-control", "placeholder": "nombre@ejemplo.com"
            }),
            "motivo": forms.Select(attrs={"class": "form-select"}),
            "mensaje": forms.Textarea(attrs={
                "class": "form-control", "rows": 3, "maxlength": 500,
                "placeholder": "Razón para contactarte (máx. 500 caracteres)"
            }),
        }
