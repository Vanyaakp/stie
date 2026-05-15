from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Повышение пользователя до статуса администратора'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            help='Имя пользователя для повышения'
        )

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Пользователь "{username}" успешно повышен до администратора!'
                )
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f'✗ Пользователь "{username}" не найден!'
                )
            )
