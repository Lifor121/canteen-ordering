from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings

class JWTCookieAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Пытаемся получить токен из cookie 'access_token'
        token = request.COOKIES.get('access_token')

        if token is None:
            return None

        # Валидируем токен
        validated_token = self.get_validated_token(token)
        
        # Получаем пользователя по валидному токену
        return self.get_user(validated_token), validated_token