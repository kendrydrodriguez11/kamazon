**Idea del Proyecto:**

FaceCommerce es un proyecto de programación diseñado para el aprendizaje universitario, inspirado en la idea de negocio de Amazon. El proyecto se enfoca en la creación de una aplicación web que permita a los usuarios registrados comprar productos de diversas categorías, así como a los vendedores publicar productos y gestionar sus ventas.

---
**Tecnologias Utilizadas:**
- Python
- Django
- HTML
- Tailwind CSS
- JavaScript
---
**Instalacion:**
1. Clonar el repositorio
```bash
https://github.com/kendrydrodriguez11/FaceCommerce.git
```
2. Instalar las dependencias
```bash
pip install -r requirements.txt
```
3. Crear database en postgres
4. Crear nuestro archivo .env, podemos crear una copia a partir del de ejemplo:
```bash
cp .env.example .env
```
5. Crear tabla cache
```bash
python manage.py createcachetable
```
6. Crear migraciones
```bash
python manage.py makemigrations / python manage.py makemigrations <app_name>
python manage.py migrate
```
7. Crear superusuario
```bash
python manage.py createsuperuser
```
8. Correr el servidor
```bash
python manage.py runserver 0.0.0.0:8000
```
