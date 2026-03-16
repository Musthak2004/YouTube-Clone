pip install -r requirements.txt --break-system-packages
mkdir -p staticfiles_build/static
python manage.py collectstatic --noinput