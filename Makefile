all: patches/*.txt nocturne_rando.exe nocturne_rando_windows.zip

patches:
	cd asm && ./armips.exe src.asm -sym2 build/sym.txt && python build.py

nocturne_rando.exe: *.py data/*.txt patches/*
	pyinstaller.exe randomizer.py -F -n nocturne_rando --add-data "data/*.txt;data" --add-data "patches;patches" --add-data "version.txt;." -i data/icon.ico
	mv -f dist/nocturne_rando.exe .
	
nocturne_rando_windows.zip: nocturne_rando.exe README.md
	zip -r nocturne_rando_windows.zip nocturne_rando.exe README.md
