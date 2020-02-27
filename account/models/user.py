from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email"), unique=True)

    troops = models.ManyToManyField(
        "troop.Troop", verbose_name=_("troops"), blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def send_welcome_email(self):
        context = {
            "user": self,
            "uid": urlsafe_base64_encode(force_bytes(self.pk)),
            "token": PasswordResetTokenGenerator().make_token(self),
        }

        msg_plain = render_to_string("account/user_welcome_email.txt", context)
        msg_html = render_to_string("account/user_welcome_email.html", context)

        # TODO: sender email address, subject, content of email
        send_mail(
            _("Welcome"),
            msg_plain,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            html_message=msg_html,
        )
