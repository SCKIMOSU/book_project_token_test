# Token 인증 DRF 기반 Book 프로젝트

- **Token 인증이 적용된 Django REST Framework(DRF)** 기반의 `Book` 예제 프로젝트.

---

## ✅ 목표

- Book 모델: 제목, 저자, 출판일 포함
- 사용자 인증: Token 기반 인증 (`rest_framework.authtoken`)
- 인증된 사용자만 Book API 접근 가능 (`IsAuthenticated`)
- 로그인 후 Token 발급 → 이후 Authorization 헤더로 접근

---

## 📁 프로젝트 구조

```
book_project/
├── book_project/         # Django 설정
│   └── settings.py
├── book/                 # Book 앱
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── users/                # 사용자 앱
│   ├── views.py
│   └── urls.py
├── manage.py

```

---

## 1️⃣ 설치 및 설정

```bash
pip install djangorestframework
pip install djangorestframework.authtoken
django-admin startproject book_project .
python manage.py startapp book
python manage.py startapp users

```

`settings.py` 수정:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
    'book',
    'users',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

```

---

## 2️⃣ Book 모델

`book/models.py`

```python
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    published_date = models.DateField()

    def __str__(self):
        return self.title

```

---

## 3️⃣ Book Serializer

`book/serializers.py`

```python
from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

```

---

## 4️⃣ Book View

`book/views.py`

```python
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Book
from .serializers import BookSerializer

class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

```

---

## 5️⃣ Book URL 설정

`book/urls.py`

```python
from django.urls import path
from .views import BookListCreateView

urlpatterns = [
    path('', BookListCreateView.as_view(), name='book-list-create'),
]

```

---

## 6️⃣ 사용자 인증 - Token 생성 및 로그인

`users/views.py`

```python
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'user_id': token.user_id})

```

`users/urls.py`

```python
from django.urls import path
from .views import CustomAuthToken

urlpatterns = [
    path('login/', CustomAuthToken.as_view(), name='login'),
]

```

---

## 7️⃣ 프로젝트 URL 연결

`book_project/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/books/', include('book.urls')),
    path('api/users/', include('users.urls')),  # login
]

```

---

## 8️⃣ 마이그레이션 및 superuser 생성

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

```

---

## 9️⃣ Token 생성 자동화

`signals.py` (users 앱에 생성)

```python
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

```

`users/apps.py` 수정:

```python
def ready(self):
    import users.signals

```

---

## 🔟 테스트

1. 로그인 → 토큰 발급:

```bash
curl -X POST http://localhost:8000/api/users/login/ \
     -d "username=admin&password=admin"

```

1. Book API 접근:

```bash
curl -H "Authorization: Token <발급된 토큰>" \
     http://localhost:8000/api/books/

```

---

## Token **테스트 방법**

- `Token 인증이 적용된 Django REST API`에서 사용할 수 있는 다양한 **테스트 방법**

---

## ✅ 1. Django Admin에서 사용자 및 Token 직접 확인

1. `python manage.py createsuperuser`
2. `python manage.py runserver`
3. 브라우저 접속: [http://localhost:8000/admin](http://localhost:8000/admin)
4. **Token**은 `Token` 모델 (`rest_framework.authtoken.models.Token`)에서 직접 생성/확인 가능

---

## ✅ 2. `curl` 명령어 테스트 (터미널 사용)

### 🔐 로그인 (토큰 발급)

```bash
curl -X POST http://127.0.0.1:8000/api/users/login/ \
     -d "username=admin&password=admin"

```

### 📘 인증된 사용자로 Book 목록 요청

```bash
curl -H "Authorization: Token <복사한_토큰>" \
     http://127.0.0.1:8000/api/books/

```

---

## ✅ 3. Postman 사용 (GUI 환경 테스트)

1. **POST** 요청: `http://127.0.0.1:8000/api/users/login/`
    - Body → `x-www-form-urlencoded`
        - `username`: `admin`
        - `password`: `admin`
2. 발급받은 `token` 확인
3. 새 요청 → **GET** `http://127.0.0.1:8000/api/books/`
    - Headers에 다음 추가:
        
        ```
        Key: Authorization
        Value: Token <토큰값>
        
        ```
        

---

## ✅ 4. Django 테스트 코드 작성

`book/tests.py`에 다음과 같이 작성할 수 있습니다:

```python
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from .models import Book

class BookAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_book_list_authenticated(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, 200)

    def test_book_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, 401)

```

실행:

```bash
python manage.py test book

```

---

## ✅ 5. 브라우저 API 자동 문서 확인

`rest_framework`는 기본적으로 웹 브라우저용 **Browsable API**를 제공합니다.

- `http://127.0.0.1:8000/api/books/` 접속 → 오른쪽 상단 로그인 → 인증된 상태로 테스트 가능

---

## ✅ 6. Swagger 또는 Redoc API 문서 연동 (선택)

```bash
pip install drf-yasg

```

`urls.py` 설정:

```python
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Book API",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

```

---

# ✅ Token 인증을 포함한 API 접근 전체 흐름

---

## 1️⃣ 인증 방식 개요

- `TokenAuthentication`은 사용자가 로그인하면 **서버가 토큰(Token)**을 발급해주고,
- 이후 API 요청 시 **HTTP Header에 토큰을 포함**하여 인증함.

---

## 2️⃣ Token 발급 (POST 요청으로 로그인)

### 🔐 요청

```bash
curl -X POST http://127.0.0.1:8000/api/users/login/ \
     -d "username=admin" \
     -d "password=1234"

```

### 📥 응답 예시

```json
{
  "token": "c12345abf87cfbb39fba7d69a91234abc12efb9c",
  "user_id": 1,
  "username": "admin"
}

```

> 이 token 값을 잘 저장해둡니다. 이후 모든 요청에 포함시켜야 합니다.
> 

---

## 3️⃣ Token 인증을 포함한 API 요청

이제 API에 접근할 때 **Authorization 헤더에 토큰을 포함**합니다.

### ✅ 헤더 형식

```
Authorization: Token <토큰값>

```

예를 들어, `books/` API에 접근하려면:

```bash
curl -H "Authorization: Token c12345abf87cfbb39fba7d69a91234abc12efb9c" \
     http://127.0.0.1:8000/api/books/

```

---

## 4️⃣ Postman 사용 방법 (GUI 환경)

1. **POST** 요청: `http://127.0.0.1:8000/api/users/login/`
    - Body → `x-www-form-urlencoded`
        - `username`: `admin`
        - `password`: `1234`
    - 응답에서 `token` 값 복사
2. **GET** 요청: `http://127.0.0.1:8000/api/books/`
    - Headers 탭:
        - Key: `Authorization`
        - Value: `Token <토큰값>`

---

## 5️⃣ Django 코드 설정 정리

### `settings.py`

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

```

### `views.py` (예시)

```python
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Book
from .serializers import BookSerializer

class BookListCreateView(ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

```

---

## 6️⃣ 인증 실패 예시

- 토큰 없이 요청하면:

```json
{
  "detail": "Authentication credentials were not provided."
}

```

- 잘못된 토큰으로 요청하면:

```json
{
  "detail": "Invalid token."
}

```

---

## ✅ 요약 정리

| 단계 | 설명 |
| --- | --- |
| 1 | 로그인 요청으로 Token 발급 (POST) |
| 2 | 이후 모든 요청에 `Authorization: Token <토큰>` 헤더 포함 |
| 3 | Django에서는 `TokenAuthentication`, `IsAuthenticated` 설정 필요 |
| 4 | Postman 또는 curl로 테스트 가능 |

---

## 🔁 전체 테스트 코드

```python
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from .models import Book

class BookAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='testpass')
        self.token, _ = Token.objects.get_or_create(user=self.user)  # ✅ 언팩
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)  # ✅ 이제 오류 없음

    def test_book_list_authenticated(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, 200)

    def test_book_list_unauthenticated(self):
        self.client.credentials()  # 인증 제거
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, 401)

```

---

## 🧪 이후 테스트 실행

```bash
python manage.py test book

```

성공 메시지:

```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..
----------------------------------------------------------------------
Ran 2 tests in 0.532s

OK

```

---

## ✅ 요약

| 문제 | 해결 방법 |
| --- | --- |
| `'tuple' object has no attribute 'key'` | `token, _ = Token.objects.get_or_create(...)` 사용 |
| `.key` 접근 | 반드시 `token` 객체에서만 접근해야 함 |
| 테스트 에러 해결 | `setUp()`에서 언팩 필수 |

---

## 🔁 전체 테스트 코드 예시

```python
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from .models import Book

class BookAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='testpass')
        self.token, _ = Token.objects.get_or_create(user=self.user)  # ✅ 언팩
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)  # ✅ 이제 오류 없음

    def test_book_list_authenticated(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, 200)

    def test_book_list_unauthenticated(self):
        self.client.credentials()  # 인증 제거
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, 401)

```

---

## 🧪 이후 테스트 실행

```bash
python manage.py test book

```

성공 메시지:

```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..
----------------------------------------------------------------------
Ran 2 tests in 0.532s

OK

```

---

## ✅ 요약

| 문제 | 해결 방법 |
| --- | --- |
| `'tuple' object has no attribute 'key'` | `token, _ = Token.objects.get_or_create(...)` 사용 |
| `.key` 접근 | 반드시 `token` 객체에서만 접근해야 함 |
| 테스트 에러 해결 | `setUp()`에서 언팩 필수 |

---
