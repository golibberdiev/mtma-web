from django.db import models
from django.contrib.auth.models import User


# ============================================================
# 1. Sinf / laboratoriyalar va ularning jihozlanganligi
# ============================================================

class Classroom(models.Model):
    """
    Sinf / laboratoriya haqida ma'lumot:
    jihozlanganlik darajasini baholash uchun bazaviy obyekt.
    """
    name = models.CharField(max_length=100)  # Masalan: "303-laboratoriya"
    building = models.CharField(
        max_length=100,
        blank=True,
        help_text="Masalan: Asosiy bino, 2-bino va h.k."
    )
    capacity = models.PositiveIntegerField(
        default=0,
        help_text="Xonaning maksimal sig'imi (talabalar soni)."
    )

    def __str__(self) -> str:
        return self.name


class Equipment(models.Model):
    """
    Har bir sinf uchun texnik jihozlanganlik ko'rsatkichlari.
    Bu yerda texnik indeksni (TJI) keyinchalik kod orqali hisoblashimiz mumkin.
    """
    classroom = models.OneToOneField(
        Classroom,
        on_delete=models.CASCADE,
        related_name="equipment"
    )

    computers_count = models.PositiveIntegerField(default=0)
    projector = models.BooleanField(default=False)
    interactive_board = models.BooleanField(default=False)
    sound_system = models.BooleanField(default=False)
    internet_speed_mbps = models.FloatField(
        default=0.0,
        help_text="Mb/s da o'lchanadi"
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Jihozlanganlik: {self.classroom.name}"


# ============================================================
# 2. O'qituvchi profili va darslar (mikrodarajadagi tahlil)
# ============================================================

class TeacherProfile(models.Model):
    """
    O'qituvchi profili: keyinchalik multimedia qo'llash
    koeffitsiyenti (MQK)ni hisoblashda ishlatiladi.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    department = models.CharField(
        max_length=150,
        blank=True,
        help_text="Masalan: Kompyuter injiniringi"
    )
    academic_title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Masalan: dotsent, katta o'qituvchi va h.k."
    )

    def __str__(self) -> str:
        return self.full_name


class Lesson(models.Model):
    """
    Dars (mavzu) bo'yicha multimedia qo'llash haqida ma'lumot.
    Har bir dars uchun multimedia koeffitsiyentini (MQK) hisoblash mumkin.
    """
    TEACHING_FORMS = (
        ("lecture", "Ma'ruza"),
        ("lab", "Laboratoriya"),
        ("practice", "Amaliy"),
        ("seminar", "Seminar"),
    )

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons"
    )

    subject = models.CharField(max_length=150)  # Masalan: "Kompyuterni tashkil etish"
    topic = models.CharField(max_length=200)    # Mavzu nomi
    date = models.DateField()

    teaching_form = models.CharField(
        max_length=20,
        choices=TEACHING_FORMS,
        default="lecture"
    )

    # Multimedia vositalari
    use_video = models.BooleanField(default=False)
    use_animation = models.BooleanField(default=False)
    use_simulation = models.BooleanField(default=False)          # Virtual laboratoriya
    use_interactive_test = models.BooleanField(default=False)
    use_ar_vr = models.BooleanField(default=False)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def multimedia_score(self) -> int:
        """
        Qanchalik ko'p turdagi multimedia qo'llansa,
        score shunchalik yuqori (0..5).
        """
        score = 0
        for field in [
            "use_video",
            "use_animation",
            "use_simulation",
            "use_interactive_test",
            "use_ar_vr",
        ]:
            if getattr(self, field):
                score += 1
        return score

    def __str__(self) -> str:
        return f"{self.subject} – {self.topic}"


class Survey(models.Model):
    """
    Talabalar uchun darsdan keyingi qisqa so'rovnoma.
    (Talaba qoniqish indeksi - TQI)
    """
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="surveys"
    )
    student_code = models.CharField(
        max_length=50,
        help_text="Talaba ID yoki shifrlangan kod"
    )

    # Likert shkalasi: 1–5
    clarity = models.PositiveSmallIntegerField()             # Mavzu tushunarliligi
    interest = models.PositiveSmallIntegerField()            # Qiziqish darajasi
    multimedia_help = models.PositiveSmallIntegerField()     # Multimedia foydaliligi
    overall_satisfaction = models.PositiveSmallIntegerField()  # Umumiy baho

    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def average_score(self) -> float:
        """
        Talaba qoniqishining o'rtacha balli (1.0–5.0).
        """
        return (
            self.clarity
            + self.interest
            + self.multimedia_help
            + self.overall_satisfaction
        ) / 4.0

    def __str__(self) -> str:
        return f"So'rovnoma – {self.lesson.subject} ({self.student_code})"


# ============================================================
# 3. Tashkilot darajasidagi ko'rsatkichlar (Dashboard uchun)
# ============================================================

class OrganizationStat(models.Model):
    """
    Dashboard’da ko‘rinadigan asosiy yig‘ma ko‘rsatkichlar.
    Bitta yozuv - bitta tashkilot (OTM / fakultet / kafedra) uchun.
    """

    name = models.CharField(
        "Tashkilot nomi",
        max_length=255,
        help_text="Masalan: ATMU, QARDU, Kompyuter injiniringi kafedrasi va h.k."
    )

    # Sinf / laboratoriya xonalari soni
    classroom_count = models.PositiveIntegerField(
        "Sinf / laboratoriya xonalari soni",
        default=0,
    )

    # Dars turlari bo‘yicha multimedia qo‘llangan mashg‘ulotlar soni
    lectures = models.PositiveIntegerField(
        "Ma'ruza darslari soni",
        default=0,
    )
    labs = models.PositiveIntegerField(
        "Laboratoriya mashg'ulotlari soni",
        default=0,
    )
    practicals = models.PositiveIntegerField(
        "Amaliy mashg'ulotlar soni",
        default=0,
    )

    # Talaba so‘rovnomalari soni (TQI uchun ma'lumotlar bazasi)
    survey_count = models.PositiveIntegerField(
        "Talaba so'rovnomalari soni",
        default=0,
    )

    # Tizim tomonidan hisoblanadigan integral ko‘rsatkich (0–100 %)
    technical_index = models.PositiveIntegerField(
        "Multimedia qo'llash indeksi (TJI, %)",
        default=0,
        help_text="Bu maydon avtomatik ravishda hisoblanadi."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tashkilot statistikasi"
        verbose_name_plural = "Tashkilot statistikasi"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    # ---------- Hosila xususiyatlar ----------

    @property
    def total_multimedia_lessons(self) -> int:
        """
        Umumiy multimedia qo'llangan darslar soni.
        """
        return self.lectures + self.labs + self.practicals

    # ---------- Hisoblash logikasi ----------

    def compute_technical_index(self) -> int:
        """
        Kiritilgan parametrlar asosida TJI ni (0–100 %) hisoblaydi.

        Uchta asosiy komponent:
        1) Xonalar yuklamasi (room_utilization)
        2) Talaba so'rovnomalari faolligi (survey_factor)
        3) Dars turlari bo'yicha xilma-xillik (variety)

        Kerak bo‘lsa, dissertatsiya modeli bo‘yicha
        og‘irlik koeffitsiyentlarini oson o‘zgartirish mumkin.
        """

        lesson_count = self.total_multimedia_lessons

        # 1) Xona yuklamasi: shartli ravishda 1 xona = 10 multimedia dars (maksimal yuklama)
        if self.classroom_count > 0:
            room_utilization = lesson_count / (self.classroom_count * 10)
        else:
            room_utilization = 0.0
        room_utilization = max(0.0, min(1.0, room_utilization))

        # 2) So'rovnomalar faolligi: 0–200 oralig'ida normallashtiramiz
        if self.survey_count > 0:
            survey_factor = min(1.0, self.survey_count / 200.0)
        else:
            survey_factor = 0.0

        # 3) Darslar xilma-xilligi: ma'ruza / lab / amaliy nechta turi ishlatilgan
        nonzero = sum(
            1 for v in (self.lectures, self.labs, self.practicals) if v > 0
        )
        variety = nonzero / 3.0  # 0, 1/3, 2/3, 1.0

        # Yakuniy ball (0–1), keyin % ga ko'paytiramiz
        score = 0.5 * room_utilization + 0.3 * survey_factor + 0.2 * variety
        return round(score * 100)

    def save(self, *args, **kwargs):
        """
        Model saqlanishidan oldin TJI ni avtomatik hisoblab yangilab qo'yamiz.
        """
        self.technical_index = self.compute_technical_index()
        super().save(*args, **kwargs)
