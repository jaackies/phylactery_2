#!/usr/bin/env sh
python manage.py collectstatic --noinput
exec "$@"