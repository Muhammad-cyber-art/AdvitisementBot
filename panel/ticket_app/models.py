from django.db import models

class ActiveChat(models.Model):
    chat_id = models.CharField(max_length=100, unique=True, verbose_name="Chat ID")
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Guruh/Kanal Nomi")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqti")

    def __str__(self):
        return f"{self.title or 'Nomsiz'} ({self.chat_id})"

    class Meta:
        verbose_name = "Faol Chat"
        verbose_name_plural = "Faol Chatlar"

class Advertisement(models.Model):
    from_city = models.CharField(max_length=100, verbose_name="Qayerdan")
    to_city = models.CharField(max_length=100, verbose_name="Qayerga")
    departure_date = models.DateField(verbose_name="Qachon (Sana)")
    price = models.CharField(max_length=50, verbose_name="Narxi")
    phone = models.CharField(max_length=20, verbose_name="Murojaat uchun tel raqam")
    telegram_username = models.CharField(max_length=50, verbose_name="Telegram Username", blank=True, null=True)
    image = models.ImageField(upload_to="ads/", verbose_name="Rasm")
    description = models.TextField(blank=True, null=True, verbose_name="Qo'shimcha izoh")
    
    is_published = models.BooleanField(default=False, verbose_name="Yuborildi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    def __str__(self):
        return f"{self.from_city} -> {self.to_city} ({self.departure_date})"

    class Meta:
        verbose_name = "E'lon (Chipta)"
        verbose_name_plural = "E'lonlar (Chiptalar)"
