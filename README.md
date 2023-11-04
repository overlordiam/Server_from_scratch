- Commands to run:
python httpc.py get -v localhost:8080/foo
python httpc.py get -v localhost:8080/
python httpc.py get -v localhost:8080/qwe.txt
python httpc.py get -v localhost:8080/../
python httpc.py get -v localhost:8080/ -H Accept:application/json
python httpc.py post -d "some new data" -v localhost:8080/foo  
python httpc.py post -d "overwrite with new data" -v -r localhost:8080/foo
python httpc.py post -d "some new data" -v -r localhost:8080/new.txt
python concurrency.py