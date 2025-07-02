### Справка по работе с API

**Аутентификация:** Система использует JWT-токены, передаваемые через `HttpOnly` cookie с именем `access_token`.
#### Регистрация нового пользователя

- **Endpoint:** `create_user`
- **Метод:** `POST`
- **URL:** `/api/v1/create_user`
- **Тело запроса (Body):**
``` JSON
    {
	    "username": "new_student",
	    "password": "strong_password_123"
	}
```

#### Авторизация (Вход)

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

#### Обновление информации о пользователе

- **Endpoint:** `update_user`
- **Метод:** `POST`
- **URL:** `/api/v1/update_user`
- **Тело запроса (Body):**
``` JSON
	{
    	"username": "existing_student",
    	"first_name": "first_name",
    	"last_name": "last_name"
	}
```

#### Получение информации о текущем пользователе

- **Endpoint:** `get_user_info`
- **Метод:** `GET`
- **URL:** `/api/v1/get_user_info`

#### Получение списка столовых
- **Endpoint:** `canteens`
- **Метод:** `GET`
- **URL:** `/api/v1/canteens`

#### Получение меню для выбранной столовой

- **Endpoint:** `canteens/<canteen_id>/menu`
- **Метод:** `GET`
- **URL:** `/api/v1/canteens/1/menu` (где `1` - это ID столовой)

#### Получение информации об одном блюде

- **Endpoint:** `canteens/<canteen_id>/menu/<dish_id>`
- **Метод:** `GET`
- **URL:** `canteens/<canteen_id>/menu/1` (где `1` - это ID блюда)
#### Создание нового заказа
- **Endpoint:** `set_order`
- **Метод:** `POST`
- **URL:** `/api/v1/set_order`
- **Тело запроса (Body):**
```JSON
	{ 
		"canteen_id": 1, 
		"items": [ 
			{ "dish_id": 1, "quantity": 2 }, 
			{ "dish_id": 3, "quantity": 1 } 
		] 
	}
```

#### Выход из системы
- **Endpoint:** `logout`
- **Метод:** `POST`
- **URL:** `/api/v1/logout`

#### Получение списка заказов
- **Endpoint:** `worker/orders`
- **Метод:** `GET`
- **URL:** `/api/v1/worker/orders`

#### Обновление статуса заказа
- **Endpoint:** `worker/orders/<order_id>/update-status`
- **Метод:** `POST`
- **URL:** `/api/v1/worker/orders/1/update-status` (где `1` - это ID блюда)
- **Тело запроса (Body):**
```JSON
	{ 
		"status": "ready"
	}