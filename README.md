### Справка по работе с API

**Аутентификация:** Система использует JWT-токены, передаваемые через `HttpOnly` cookie с именем `access_token`.
#### 1. Регистрация нового пользователя

- **Endpoint:** `create_user`
- **Метод:** `POST`
- **URL:** `/api/v1/create_user`
- **Тело запроса (Body):**
``` JSON
    {
	    "username": "new_student",
	    "password": "strong_password_123",
	    "password2": "strong_password_123"
	}
```

#### 2. Авторизация (Вход)

- **Endpoint:** `authorization`
- **Метод:** `POST`
- **URL:** `/api/v1/authorization`
- **Тело запроса (Body):**
``` JSON
{
    "username": "existing_student",
    "password": "strong_password_123"
}
```

#### 3. Получение информации о текущем пользователе

- **Endpoint:** `get_user_info`
- **Метод:** `GET`
- **URL:** `/api/v1/get_user_info`

#### 4. Получение списка всех доступных блюд
- **Endpoint:** `get_dishes_info`
- **Метод:** `GET`
- **URL:** `/api/v1/get_dishes_info`

#### 5. Получение информации о конкретном блюде

- **Endpoint:** `get_dish_info/id`
- **Метод:** `GET`
- **URL:** `/api/v1/get_dish_info/1` (где `1` - это ID блюда)

#### 6. Создание нового заказа
- **Endpoint:** `set_order`
- **Метод:** `POST`
- **URL:** `/api/v1/set_order`
- **Тело запроса (Body):**
```JSON
{ 
	"items": [ 
		{ "dish_id": 1, "quantity": 2 }, 
		{ "dish_id": 3, "quantity": 1 } 
	] 
}
```

#### 7. Выход из системы
- **Endpoint:** `logout`
- **Метод:** `POST`
- **URL:** `/api/v1/logout`