NUMCORES=$(nproc)
WORKERS=$(( $NUMCORES * 2 ))
/home/ubuntu/API/venv/bin/gunicorn main:app -k uvicorn.workers.UvicornWorker --workers $WORKERS