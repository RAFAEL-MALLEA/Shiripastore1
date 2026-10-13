import django.db.models.deletion
import django.utils.timezone
import venta.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('Id_categoria', models.AutoField(db_column='idCategoria', primary_key=True, serialize=False)),
                ('categoria', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Categorías',
                'ordering': ['categoria'],
            },
        ),
        migrations.CreateModel(
            name='Coleccion',
            fields=[
                ('Id_coleccion', models.AutoField(db_column='idColeccion', primary_key=True, serialize=False)),
                ('coleccion', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Colecciones',
                'ordering': ['coleccion'],
            },
        ),
        migrations.CreateModel(
            name='Plataforma',
            fields=[
                ('Id_plataforma', models.AutoField(db_column='idPlataforma', primary_key=True, serialize=False)),
                ('plataforma', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Plataformas',
                'ordering': ['plataforma'],
            },
        ),
        migrations.CreateModel(
            name='Inventario',
            fields=[
                ('Id_juego', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_juego', models.CharField(max_length=60)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=8)),
                ('stock', models.PositiveIntegerField(default=100)),
                ('disponible', models.BooleanField(default=True)),
                ('imagen', models.CharField(blank=True, help_text='Nombre del archivo dentro de venta/static/IMG/', max_length=150)),
                ('Id_categoria', models.ForeignKey(db_column='idCategoria', on_delete=django.db.models.deletion.CASCADE, related_name='juegos', to='venta.categoria')),
                ('Id_coleccion', models.ForeignKey(db_column='idColeccion', on_delete=django.db.models.deletion.CASCADE, related_name='juegos', to='venta.coleccion')),
                ('Id_plataforma', models.ForeignKey(db_column='idPlataforma', on_delete=django.db.models.deletion.CASCADE, related_name='juegos', to='venta.plataforma')),
            ],
            options={
                'verbose_name_plural': 'Inventario',
                'ordering': ['nombre_juego'],
            },
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_boleta', models.CharField(default=venta.models.generar_codigo_boleta, editable=False, max_length=20, unique=True)),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('estado', models.CharField(choices=[('pagado_simulado', 'Pago simulado aprobado'), ('cancelado', 'Cancelado')], default='pagado_simulado', max_length=20)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedidos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='MensajeContacto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('motivo', models.CharField(choices=[('soporte', 'Soporte técnico'), ('reclamo', 'Reclamo'), ('sugerencia', 'Sugerencia'), ('otro', 'Otro')], max_length=20)),
                ('mensaje', models.TextField(max_length=500)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('atendido', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='DetallePedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_juego', models.CharField(max_length=60)),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=8)),
                ('inventario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='venta.inventario')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='venta.pedido')),
            ],
        ),
    ]
