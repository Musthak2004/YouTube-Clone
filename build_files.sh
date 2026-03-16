pip install -r requirements.txt --break-system-packages
python manage.py collectstatic --noinput
mkdir -p staticfiles_build/static