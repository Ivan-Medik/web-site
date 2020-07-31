from django.db import models
from django.urls import reverse


class Products(models.Model):
	
	name = models.CharField("Название", max_length=150)
	category = models.CharField("Категория", max_length=150)
	description = models.TextField("Описание")
	background = models.CharField("Цвет фона", max_length=150)
	image = models.ImageField("Фото", upload_to="products/")
	count = models.PositiveIntegerField("Количество", default=0)
	kkal = models.PositiveIntegerField("Количество ккал", default=0)
	price = models.PositiveIntegerField("Цена", default=0, help_text="указывать сумму в рублях")

	def __str__(self):

		return self.name

	class Meta:

		verbose_name = "Продукт"
		verbose_name_plural = "Продукты"
