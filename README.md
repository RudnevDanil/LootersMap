# LootersMap

из папки studying_js/2 looters map preview зауск php сервера
	php -S localhost:8000 -t "./"
	
mysql стартует автоматически

сайт по адресу localhost:8000

cpp запускается из папки release из консоли командой
	LootersMap_cpp_linux

файл video_to_snaps.py может быть запущен только вручную командой ниже. Данный файл перегоняет видео из директории video_for_classification в картинки и имитирует работу камер.
	python3  video_to_snaps.py

 В директории release для работы должны пристутствовать пустые папки 
 	faces 
 	saved_imgs 
 	saved_video 
 	video_for_classification
 	
 В процессе работы они могут наполняться и опустошаться, это может повлиять на гитхаб, однако в них нельзя хранить ничего и они обязаны быть!
