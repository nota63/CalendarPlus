#!/bin/bash
# build_files.sh
#!/bin/bash
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Cleaning up migrations (optional)..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
