docker run --name test -d -p 9000:9000 joshjamison/ignition
python scripts/time_wait.py
curl http://127.0.0.1:9000/
