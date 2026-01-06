from django.db import models
from django.utils import timezone


class PostQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(
            is_published=True,
            pub_date__lte=now,
            category__is_published=True
        ).filter(
            models.Q(location__is_published=True) | models.Q(
                location__isnull=True
            )
        )

    def visible_to(self, user):
        if user.is_authenticated:
            return self.filter(
                models.Q(author=user) | models.Q(pk__in=self.published())
            )
        return self.published()


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db).select_related(
            'author', 'category', 'location'
        )

    def published(self):
        return self.get_queryset().published()

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)
