# monitoring/views.py

from django.shortcuts import render, redirect
from .models import OrganizationStat
from django.utils import timezone
import json


def _to_int(value, default=0):
    """POST dan kelgan qiymatni xavfsiz int ga aylantirish."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def dashboard(request):
    """
    Asosiy dashboard sahifasi.
    Oxirgi OrganizationStat yozuvini olib, undan barcha ko'rsatkichlarni hisoblaydi.
    """
    stat = OrganizationStat.objects.order_by("-created_at").first()

    if not stat:
        # hech qanday yozuv bo'lmasa – minimal default holat
        context = {
            "org_name": "Tashkilot nomi kiritilmagan",
            "classroom_count": 0,
            "lesson_count": 0,
            "survey_count": 0,
            "avg_multimedia_score": 0,
            "summary_text": "Hali parametrlar kiritilmagan. Tashkilot sozlamalari sahifasida ma'lumotlar kiriting.",
            "tji_labels_json": json.dumps([], ensure_ascii=False),
            "tji_values_json": json.dumps([], ensure_ascii=False),
            "lesson_labels_json": json.dumps([], ensure_ascii=False),
            "lesson_values_json": json.dumps([], ensure_ascii=False),
        }
        return render(request, "monitoring/dashboard.html", context)

    # --- Asosiy ko‘rsatkichlar ---
    org_name = stat.name or "Tashkilot nomi kiritilmagan"
    total_multimedia_lessons = stat.total_multimedia_lessons
    technical_index = stat.technical_index

    # --- Xulosa matni ---
    if technical_index >= 80:
        level_comment = (
            "multimedia jihozlardan foydalanish darajasi juda yuqori, mavjud yutuqlarni mustahkamlash tavsiya etiladi."
        )
    elif technical_index >= 60:
        level_comment = (
            "multimedia qo‘llashning texnik ko‘rsatkichi 60–79 % oralig‘ida, bu holat o‘rtacha–yaxshi darajada baholanadi."
        )
    elif technical_index >= 40:
        level_comment = (
            "multimedia vositalaridan foydalanish yetarli emas, ayrim yo‘nalishlarda texnik bazani kuchaytirish zarur."
        )
    else:
        level_comment = (
            "multimedia resurslaridan foydalanish past darajada, ustuvor ravishda texnik jihozlash va metodik ko‘makni oshirish kerak."
        )

    summary_text = (
        f"Hisob-kitoblarga ko‘ra, multimedia qo‘llashning texnik ko‘rsatkichi {technical_index} % bo‘lib, "
        f"bu holat {level_comment}"
    )

    # --- TJI dinamikasi (oxirgi 6 yozuv) ---
    stats = OrganizationStat.objects.order_by("-created_at")[:6][::-1]
    tji_labels = [s.created_at.strftime("%b") if s.created_at else "?" for s in stats]
    tji_values = [s.technical_index for s in stats]

    # --- Dars turlari bo‘yicha taqsimot ---
    distribution_labels = []
    distribution_values = []
    for name, value in [
        ("Ma'ruza", stat.lectures),
        ("Laboratoriya", stat.labs),
        ("Amaliy", stat.practicals),
    ]:
        if value > 0:
            distribution_labels.append(name)
            distribution_values.append(value)

    context = {
        "org_name": org_name,
        "classroom_count": stat.classroom_count,

        # kartochkalar uchun:
        "lesson_count": total_multimedia_lessons,       # Multimedia darslar
        "survey_count": stat.survey_count,              # Talaba so‘rovnomalari
        "avg_multimedia_score": technical_index,        # Multimedia qo‘llash (texnik)

        # xulosa:
        "summary_text": summary_text,

        # grafiklar uchun:
        "tji_labels_json": json.dumps(tji_labels, ensure_ascii=False),
        "tji_values_json": json.dumps(tji_values, ensure_ascii=False),
        "lesson_labels_json": json.dumps(distribution_labels, ensure_ascii=False),
        "lesson_values_json": json.dumps(distribution_values, ensure_ascii=False),
    }

    return render(request, "monitoring/dashboard.html", context)
def org_settings(request):
    """
    Tashkilot sozlamalari sahifasi.
    Shu yerda kiritilgan ma'lumotlar OrganizationStat ga yoziladi
    va dashboard shunga qarab yangilanadi.
    """
    # Oxirgi yozuvni olamiz (bitta tashkilot uchun yetarli)
    stat = OrganizationStat.objects.order_by("-created_at").first()

    if request.method == "POST":
        # Agar hali yozuv bo'lmasa – yangisini yaratamiz
        if stat is None:
            stat = OrganizationStat()

        # Formadagi qiymatlarni o'qish
        stat.name = request.POST.get("name") or None
        stat.classroom_count = _to_int(request.POST.get("classroom_count"))
        stat.lectures = _to_int(request.POST.get("lectures"))
        stat.labs = _to_int(request.POST.get("labs"))
        stat.practicals = _to_int(request.POST.get("practicals"))
        stat.survey_count = _to_int(request.POST.get("survey_count"))

        # Vaqtni yangilab qo'yamiz (dinamika uchun)
        stat.created_at = timezone.now()

        # Modelning o'zidagi formula bo'yicha technical_index hisoblanadi (agar save() yoki boshqa joyda yozilgan bo'lsa)
        stat.save()

        # Saqlangandan keyin dashboardga qaytish mumkin
        return redirect("dashboard")   # yoki "org_settings" desangiz o'sha sahifada qoladi

    # GET so'rov uchun – mavjud stat ni yoki None ni yuboramiz
    context = {"stat": stat}
    return render(request, "monitoring/org_settings.html", context)

