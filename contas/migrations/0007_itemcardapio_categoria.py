# Generated by Django 5.1.3 on 2024-11-30 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0006_pedido_categoria_itemcardapio'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemcardapio',
            name='categoria',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
    ]