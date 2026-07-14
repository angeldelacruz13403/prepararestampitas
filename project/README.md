# Cruz Cofrade

Aplicación Flask para fotografía profesional de Semana Santa, con panel administrativo, galería dinámica, SEO técnico y base de datos MariaDB.

## Requisitos
- Python 3.12+
- MariaDB 10.6+
- Nginx + Gunicorn (producción)

## Instalación
```bash
cd project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Configuración de base de datos
1. Crea base de datos `cruzcofrade` en MariaDB.
2. Ajusta `DATABASE_URL` en `.env`.
3. Ejecuta migraciones:
```bash
flask --app run.py db init
flask --app run.py db migrate -m "initial"
flask --app run.py db upgrade
```

## Ejecución local
```bash
flask --app run.py run --debug
```

## Producción (Gunicorn)
```bash
gunicorn -w 4 -b 127.0.0.1:8000 run:app
```

## Estructura
- `app/`: núcleo Flask (factory, blueprints, modelos, servicios, forms)
- `migrations/`: migraciones Flask-Migrate
- `instance/`: configuración local y archivos de runtime

## Seguridad aplicada
- CSRF global con Flask-WTF
- Contraseñas con hashing seguro
- Validación estricta de subida de imágenes
- Sesiones seguras configurables por entorno
- Protección básica de rate limit por IP en login/contacto

## SEO implementado
- Meta title/description dinámicos
- Canonical, OpenGraph, Twitter Cards
- JSON-LD Organization + Gallery breadcrumb
- `sitemap.xml` dinámico
- `robots.txt`
