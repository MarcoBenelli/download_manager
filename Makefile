dist/download_manager : src/*.py
	pyinstaller --onefile src/download_manager.py

requirements.txt : FORCE
	python -m pip freeze > requirements.txt
FORCE :

install :
	python -m pip install -r requirements.txt

clean :
	rm -rf build dist ./*.spec

.PHONY : clean install
