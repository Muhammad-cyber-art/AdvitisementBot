import os
import sys
from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib import admin
from django.contrib import messages

from .models import ActiveChat, Advertisement, GovServiceAnnouncement, ProductAnnouncement, JobAnnouncement

# Loyiha ildizini sys.path ga qo'shamiz (core, publishers modullari uchun)
_parent_dir = os.path.dirname(settings.BASE_DIR)
if _parent_dir not in sys.path:
    sys.path.append(_parent_dir)

from core.config import Config
from publishers.telegram import TelegramPublisher


# ---------------------------------------------------------------------------
# Umumiy Mixin — takrorlanishni yo'q qiladi
# ---------------------------------------------------------------------------

class TelegramPublishMixin:
    """
    Har bir e'lon Admin klassi shu mixindan meros oladi.
    Faqat `build_caption(obj)` metodini qayta yozish kerak.
    """

    def build_caption(self, obj) -> str:
        """Subklasslar bu metodni majburiy override qiladi."""
        raise NotImplementedError("build_caption() metodi implement qilinmagan.")

    def get_photo_path(self, obj) -> str | None:
        """Ob'yektda image maydoni bo'lsa, uning yo'lini qaytaradi."""
        image = getattr(obj, "image", None)
        if image and image.name:
            return image.path
        return None

    def save_model(self, request, obj, form, change):
        # Ob'yektni DBga saqlaymiz (yangi yoki tahrirlangan)
        super().save_model(request, obj, form, change)

        # Faol chatlarni olamiz
        db_chat_ids = list(ActiveChat.objects.values_list("chat_id", flat=True))
        if not db_chat_ids:
            self.message_user(
                request,
                "⚠️ Bazada hech qanday faol chat topilmadi. Yuborish bekor qilindi.",
                level=messages.WARNING,
            )
            return

        caption = self.build_caption(obj)
        photo_path = self.get_photo_path(obj)

        chats_file_path = os.path.join(_parent_dir, "active_chats.json")
        publisher = TelegramPublisher(bot_token=Config.TELEGRAM_BOT_TOKEN, chats_file=chats_file_path)

        try:
            success = async_to_sync(publisher.publish)(
                content=caption,
                photo=photo_path,
                chat_ids=db_chat_ids,
            )
            if success:
                obj.is_published = True
                obj.save(update_fields=["is_published"])
                action = "qayta yuborildi" if change else "yuborildi"
                self.message_user(
                    request,
                    f"✅ E'lon {len(db_chat_ids)} ta chatga muvaffaqiyatli {action}!",
                    level=messages.SUCCESS,
                )
            else:
                self.message_user(
                    request,
                    "❌ Yuborishda xatolik yuz berdi. Telegram API javobini tekshiring.",
                    level=messages.ERROR,
                )
        except Exception as exc:
            self.message_user(
                request,
                f"❌ Publisher bilan ulanishda xatolik: {exc}",
                level=messages.ERROR,
            )


# ---------------------------------------------------------------------------
# Faol Chatlar
# ---------------------------------------------------------------------------

@admin.register(ActiveChat)
class ActiveChatAdmin(admin.ModelAdmin):
    list_display = ("title", "chat_id", "added_at")
    search_fields = ("title", "chat_id")
    readonly_fields = ("added_at",)


# ---------------------------------------------------------------------------
# ✈️ Chipta E'loni
# ---------------------------------------------------------------------------

@admin.register(Advertisement)
class AdvertisementAdmin(TelegramPublishMixin, admin.ModelAdmin):
    list_display = ("from_city", "to_city", "departure_date", "price", "is_published", "created_at")
    list_filter = ("is_published", "departure_date")
    search_fields = ("from_city", "to_city", "phone")
    readonly_fields = ("is_published", "created_at")

    fieldsets = (
        ("✈️ Yo'nalish ma'lumotlari", {
            "fields": ("from_city", "to_city", "departure_date", "price"),
        }),
        ("📞 Aloqa", {
            "fields": ("phone", "telegram_username"),
        }),
        ("🖼️ Qo'shimcha", {
            "fields": ("image", "description"),
        }),
        ("📊 Holat", {
            "fields": ("is_published", "created_at"),
        }),
    )

    def build_caption(self, obj) -> str:
        lines = [
            "✈️ <b>Yangi Chipta E'loni!</b>\n",
            f"🛫 <b>Yo'nalish:</b> {obj.from_city} ➔ {obj.to_city}",
            f"📅 <b>Sana:</b> {obj.departure_date.strftime('%Y-%m-%d')}",
            f"💰 <b>Narxi:</b> {obj.price}",
            f"\n📞 <b>Murojaat uchun tel:</b> {obj.phone}",
        ]
        if obj.telegram_username:
            lines.append(f"💬 <b>Telegram:</b> @{obj.telegram_username.lstrip('@')}")
        if obj.description:
            lines.append(f"\n📝 <b>Qo'shimcha izoh:</b>\n{obj.description}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 🏛️ Davlat Xizmatlari E'loni
# ---------------------------------------------------------------------------

@admin.register(GovServiceAnnouncement)
class GovServiceAdmin(TelegramPublishMixin, admin.ModelAdmin):
    list_display = ("service_name", "ministry", "phone", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("service_name", "ministry", "phone")
    readonly_fields = ("is_published", "created_at")

    fieldsets = (
        ("🏛️ Xizmat ma'lumotlari", {
            "fields": ("service_name", "ministry", "description"),
        }),
        ("📍 Joylashuv va vaqt", {
            "fields": ("address", "working_hours"),
        }),
        ("📞 Aloqa", {
            "fields": ("phone", "website"),
        }),
        ("🖼️ Qo'shimcha", {
            "fields": ("image",),
        }),
        ("📊 Holat", {
            "fields": ("is_published", "created_at"),
        }),
    )

    def build_caption(self, obj) -> str:
        lines = [
            "🏛️ <b>Davlat Xizmati E'loni!</b>\n",
            f"📋 <b>Xizmat:</b> {obj.service_name}",
            f"🏢 <b>Idora / Vazirlik:</b> {obj.ministry}",
            f"📍 <b>Manzil:</b> {obj.address}",
            f"🕐 <b>Ish vaqti:</b> {obj.working_hours}",
            f"📞 <b>Telefon:</b> {obj.phone}",
        ]
        if obj.website:
            lines.append(f"🌐 <b>Veb-sayt:</b> {obj.website}")
        lines.append(f"\n📝 <b>Tavsif:</b>\n{obj.description}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 🛒 Mahsulot E'loni
# ---------------------------------------------------------------------------

@admin.register(ProductAnnouncement)
class ProductAdmin(TelegramPublishMixin, admin.ModelAdmin):
    list_display = ("product_name", "category", "condition", "price", "location", "is_published", "created_at")
    list_filter = ("is_published", "condition")
    search_fields = ("product_name", "category", "phone", "location")
    readonly_fields = ("is_published", "created_at")

    fieldsets = (
        ("🛒 Mahsulot ma'lumotlari", {
            "fields": ("product_name", "category", "condition", "price", "description"),
        }),
        ("📍 Joylashuv", {
            "fields": ("location",),
        }),
        ("📞 Aloqa", {
            "fields": ("phone", "telegram_username"),
        }),
        ("🖼️ Rasm", {
            "fields": ("image",),
        }),
        ("📊 Holat", {
            "fields": ("is_published", "created_at"),
        }),
    )

    def build_caption(self, obj) -> str:
        condition_label = dict(ProductAnnouncement.CONDITION_CHOICES).get(obj.condition, obj.condition)
        lines = [
            "🛒 <b>Mahsulot E'loni!</b>\n",
            f"📦 <b>Mahsulot:</b> {obj.product_name}",
            f"🏷️ <b>Toifa:</b> {obj.category}",
            f"✅ <b>Holati:</b> {condition_label}",
            f"💰 <b>Narxi:</b> {obj.price}",
            f"📍 <b>Joylashuv:</b> {obj.location}",
            f"\n📞 <b>Telefon:</b> {obj.phone}",
        ]
        if obj.telegram_username:
            lines.append(f"💬 <b>Telegram:</b> @{obj.telegram_username.lstrip('@')}")
        lines.append(f"\n📝 <b>Tavsif:</b>\n{obj.description}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 💼 Ish O'rin E'loni
# ---------------------------------------------------------------------------

@admin.register(JobAnnouncement)
class JobAdmin(TelegramPublishMixin, admin.ModelAdmin):
    list_display = ("position", "company", "employment_type", "location", "is_published", "created_at")
    list_filter = ("is_published", "employment_type")
    search_fields = ("position", "company", "phone", "location")
    readonly_fields = ("is_published", "created_at")

    fieldsets = (
        ("💼 Vakansiya ma'lumotlari", {
            "fields": ("position", "company", "employment_type", "salary"),
        }),
        ("📋 Talablar", {
            "fields": ("requirements",),
        }),
        ("📍 Joylashuv", {
            "fields": ("location", "deadline"),
        }),
        ("📞 Aloqa", {
            "fields": ("phone", "telegram_username"),
        }),
        ("🖼️ Qo'shimcha", {
            "fields": ("image",),
        }),
        ("📊 Holat", {
            "fields": ("is_published", "created_at"),
        }),
    )

    def build_caption(self, obj) -> str:
        employment_label = dict(JobAnnouncement.EMPLOYMENT_TYPE_CHOICES).get(obj.employment_type, obj.employment_type)
        lines = [
            "💼 <b>Ish O'rin E'loni!</b>\n",
            f"🎯 <b>Lavozim:</b> {obj.position}",
            f"🏢 <b>Kompaniya:</b> {obj.company}",
            f"⏰ <b>Ish turi:</b> {employment_label}",
        ]
        if obj.salary:
            lines.append(f"💰 <b>Maosh:</b> {obj.salary}")
        lines.append(f"📍 <b>Joylashuv:</b> {obj.location}")
        lines.append(f"\n📋 <b>Talablar va vazifalar:</b>\n{obj.requirements}")
        lines.append(f"\n📞 <b>Telefon:</b> {obj.phone}")
        if obj.telegram_username:
            lines.append(f"💬 <b>Telegram:</b> @{obj.telegram_username.lstrip('@')}")
        if obj.deadline:
            lines.append(f"📅 <b>Ariza topshirish muddati:</b> {obj.deadline.strftime('%Y-%m-%d')}")
        return "\n".join(lines)
