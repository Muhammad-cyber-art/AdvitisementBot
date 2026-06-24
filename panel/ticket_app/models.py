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
        return f"{self.from_city} → {self.to_city} ({self.departure_date})"

    class Meta:
        verbose_name = "E'lon (Chipta)"
        verbose_name_plural = "E'lonlar (Chiptalar)"


class GovServiceAnnouncement(models.Model):
    """Davlat xizmatlari haqida e'lon."""

    service_name = models.CharField(max_length=200, verbose_name="Xizmat nomi")
    ministry = models.CharField(max_length=200, verbose_name="Idora / Vazirlik")
    address = models.CharField(max_length=300, verbose_name="Manzil")
    working_hours = models.CharField(max_length=100, verbose_name="Ish vaqti", help_text="Masalan: Du–Ju 09:00–18:00")
    phone = models.CharField(max_length=20, verbose_name="Telefon raqam")
    website = models.URLField(blank=True, null=True, verbose_name="Veb-sayt", help_text="Ixtiyoriy")
    description = models.TextField(verbose_name="Tavsif")
    image = models.ImageField(upload_to="gov_services/", blank=True, null=True, verbose_name="Rasm (ixtiyoriy)")
    is_published = models.BooleanField(default=False, verbose_name="Yuborildi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    def __str__(self):
        return f"{self.service_name} — {self.ministry}"

    class Meta:
        verbose_name = "Davlat Xizmati E'loni"
        verbose_name_plural = "Davlat Xizmatlari E'lonlari"


class ProductAnnouncement(models.Model):
    """Mahsulot sotuviga e'lon."""

    CONDITION_CHOICES = [
        ("new", "Yangi"),
        ("used", "Ishlatilgan"),
        ("like_new", "Yangiday"),
    ]

    product_name = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    category = models.CharField(max_length=100, verbose_name="Toifa", help_text="Masalan: Elektronika, Kiyim, Mebel …")
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default="new", verbose_name="Holati")
    price = models.CharField(max_length=50, verbose_name="Narxi")
    location = models.CharField(max_length=200, verbose_name="Joylashuv / Shahar")
    phone = models.CharField(max_length=20, verbose_name="Telefon raqam")
    telegram_username = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telegram username")
    description = models.TextField(verbose_name="Tavsif")
    image = models.ImageField(upload_to="products/", verbose_name="Rasm")
    is_published = models.BooleanField(default=False, verbose_name="Yuborildi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    def __str__(self):
        return f"{self.product_name} — {self.price}"

    class Meta:
        verbose_name = "Mahsulot E'loni"
        verbose_name_plural = "Mahsulot E'lonlari"


class JobAnnouncement(models.Model):
    """Ish o'rin (vakansiya) e'loni."""

    EMPLOYMENT_TYPE_CHOICES = [
        ("full_time", "To'liq stavka"),
        ("part_time", "Qisman stavka"),
        ("remote", "Masofadan"),
        ("contract", "Shartnoma asosida"),
        ("internship", "Amaliyot (Staj)"),
    ]

    position = models.CharField(max_length=200, verbose_name="Lavozim nomi")
    company = models.CharField(max_length=200, verbose_name="Kompaniya / Ish beruvchi")
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default="full_time",
        verbose_name="Ish turi",
    )
    salary = models.CharField(max_length=100, blank=True, null=True, verbose_name="Maosh", help_text="Ixtiyoriy. Masalan: 3 000 000 – 5 000 000 UZS")
    location = models.CharField(max_length=200, verbose_name="Joylashuv / Shahar")
    requirements = models.TextField(verbose_name="Talablar va vazifalar")
    phone = models.CharField(max_length=20, verbose_name="Telefon raqam")
    telegram_username = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telegram username")
    deadline = models.DateField(blank=True, null=True, verbose_name="Ariza topshirish muddati", help_text="Ixtiyoriy")
    image = models.ImageField(upload_to="jobs/", blank=True, null=True, verbose_name="Banner / Logotip (ixtiyoriy)")
    is_published = models.BooleanField(default=False, verbose_name="Yuborildi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    def __str__(self):
        return f"{self.position} — {self.company}"

    class Meta:
        verbose_name = "Ish O'rin E'loni"
        verbose_name_plural = "Ish O'rin E'lonlari"


class SimpleMessage(models.Model):
    """Oddiy xabar e'loni."""

    text = models.TextField(verbose_name="Xabar matni")
    image = models.ImageField(upload_to="simple_messages/", blank=True, null=True, verbose_name="Rasm (ixtiyoriy)")
    is_published = models.BooleanField(default=False, verbose_name="Yuborildi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    def __str__(self):
        return f"Xabar: {self.text[:50]}..."

    class Meta:
        verbose_name = "Oddiy Xabar"
        verbose_name_plural = "Oddiy Xabarlar"

