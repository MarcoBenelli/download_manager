ifeq ($(OS),Windows_NT)
	target = dist/download_manager/download_manager.exe
	option = --windowed
else
	target = dist/download_manager
	option = --onefile
	rm_option = -f
endif

objects = src/app.py src/download_manager.py src/history_frame.py src/model.py

$(target) : $(objects)
	pyinstaller $(option) src/download_manager.py

requirements.txt : FORCE
	python -m pip freeze >requirements.txt
FORCE :

install :
	python -m pip install --requirement requirements.txt

clean :
	-rm -R $(rm_option) build
	-rm -R $(rm_option) dist
	-rm -R $(rm_option) ./*.spec
	-rm -R $(rm_option) Output

.PHONY : clean install
