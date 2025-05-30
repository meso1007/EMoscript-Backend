# Generated by Django 5.2 on 2025-05-09 10:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_customuser_is_locked"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="is_premium",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="bio",
            field=models.TextField(blank=True, default="じこしょうかいはまだないよ！", null=True),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="image",
            field=models.ImageField(
                blank=True,
                default="profile_images/profile-default.png",
                null=True,
                upload_to="profile_images/",
            ),
        ),
    ]
