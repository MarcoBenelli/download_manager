dist/download_manager : src/*.py
	pyinstaller --onefile src/download_manager.py

.PHONY : clean
clean :
	rm -rf build dist ./*.spec
