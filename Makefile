all: nocturne_rando.exe nocturne_rando_windows.zip

nocturne_rando.exe: *.py data/* patches/*
	pyinstaller.exe randomizer.py -F -n nocturne_rando --add-data "data;data" --add-data "patches;patches"
	mv -f dist/nocturne_rando.exe .
	
nocturne_rando_windows.zip: nocturne_rando.exe README.md
	zip -r nocturne_rando_windows.zip nocturne_rando.exe README.md
