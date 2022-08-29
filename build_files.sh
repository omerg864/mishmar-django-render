# build_files.sh
cat requirements.txt | xargs -n 1 pip install
python3.9 manage.py collectstatic