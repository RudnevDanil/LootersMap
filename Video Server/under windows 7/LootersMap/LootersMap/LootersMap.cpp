// LootersMap.cpp: определяет точку входа для консольного приложения.
// Настройка OpenCV тут https://www.opencv-srf.com/2017/11/install-opencv-with-visual-studio.html
// На схеме проекта это приложение обозначено как VideoServer
// Захватывает видео с камер соглавно настройкам, захватывает необходимое и передает дальше необходимую часть информации. 
// Что необходимо передавать и находить определяют настройки.
// Приложение многопоточное, каждая камера работает в своем потоке.
// Принцип приложения - один запуск на 100 лет работы. Ошибки и перенастройки должны происходить без остановки всего приложения.
// Желательно использовать отдельные потоки на отдельные задачи на случай подвисания процесса. Главный поток занимается ТОЛЬКО менеджментом задач между потоками (для стабильности)
// Каждый поток пишет инфу в свой log файл. Все логи в каталоге logs.

#include "stdafx.h"
#include <opencv2/opencv.hpp>
#include <windows.h>
#include <iostream>
#include <fstream>
#include <string>
#include <thread>
#include <map>


using namespace cv;
using namespace std;

string log_directory = "./log/";
map <string, string> settings;

// Контролирует чтобы дескриторы не пересекались.
class individual_descriptor
{
private:
	int next_will_be;

public:
	individual_descriptor()
	{
		next_will_be = 1;
	}

	int next()
	{
		return next_will_be++;
	}
};

// Обобщение информации по потоку видеозахвата. Хранит всевозможноые настройки, касающиеся каждого потока.
class stream_info
{
public:
	string path_to_cam;			// полный пусть по которому VideoCapture сможет получить доступ
	string path_to_saving_video;// дирректория для сохранения видео
	string path_to_saving_imgs;	// дирректория для сохранения изображений
	int skip_frames_saving;		// столько кадров будет пропущено при сохранении видео
	int skip_frames_classify;	// столько кадров будет пропущено при классификации кадров
	int fps;					// какое fps будет указано к анотации к видео
	int stream_descr;			// Дескриптор стриминга. Служит для разделения лог файлов, файлов видео и прочего. у каждого стриминга индивидуальный.
	bool is_show_on_screen;		// Показывать ли стрим на экране

	stream_info(string path_to_cam, int fps, int skip_frames_saving, int skip_frames_classify, string path_to_saving_video, string path_to_saving_imgs, int stream_descr, bool is_show_on_screen)
	{
		this->path_to_cam = path_to_cam;
		this->fps = fps;
		this->path_to_saving_video = path_to_saving_video;
		this->path_to_saving_imgs = path_to_saving_imgs;
		this->skip_frames_saving = skip_frames_saving;
		this->skip_frames_classify = skip_frames_classify;
		this->stream_descr = stream_descr;
		this->is_show_on_screen = is_show_on_screen;
	}
};

// Обновление настроек settings из xml файла
void update_settings(string path, bool is_print_map);

// Захват видео, отделение изображений(реализовать) и запрос классификации(реализовать)
int capture_cam(stream_info *info);

// Логирование информации в соответствующем потоку файле
void log(string full_file_path, string message, bool is_cout = false);

int main()
{
	// отчистить лог дирректорию.
	system("del /q \"log\"");
	system("del /q \"saved_imgs\"");

	// чтение массива настроек
	cout << "update_settings" << endl;
	update_settings("xml/settings.xml", true);
	cout << "update_settings DONE" << endl << endl;
	
	// Захват видео
	cout << endl << endl << "capture ..." << endl;
	string path_to_saving_video = "./saved_video/";
	string path_to_saving_imgs = "./saved_imgs/";
	individual_descriptor descriptors;

	// Заполнение информации о потоках захвата
	stream_info *stream_1 = new stream_info("rtsp://admin:admin@192.168.144.200:554/snl/live/1/1", 25, 25, 25, path_to_saving_video, path_to_saving_imgs, descriptors.next(), true);
	stream_info *stream_2 = new stream_info("rtsp://admin:admin@192.168.144.200:554/snl/live/1/1", 25, 25, 25, path_to_saving_video, path_to_saving_imgs, descriptors.next(), true);
	stream_info *stream_3 = new stream_info("rtsp://admin:admin@192.168.144.200:554/snl/live/1/1", 25, 25, 25, path_to_saving_video, path_to_saving_imgs, descriptors.next(), true);
	
	// Создание потоков захвата
	thread thread1(capture_cam, stream_1);
	//thread thread2(capture_cam, stream_2);
	//thread thread3(capture_cam, stream_3);

	






	/*
	//															test opencv
	// Read the image file
	Mat image = imread("D:/My OpenCV Website/Eagle.jpg");

	if (image.empty()) // Check for failure
	{
		cout << "Could not open or find the image" << endl;
		system("pause"); //wait for any key press
		return -1;
	}

	String windowName = "My HelloWorld Window"; //Name of the window

	namedWindow(windowName); // Create a window

	imshow(windowName, image); // Show our image inside the created window.

	waitKey(0); // Wait for any keystroke in the window

	destroyWindow(windowName); //destroy the created window
	*/

	

	// Ожидание завершения дочерних потоков.
	thread1.join();
	//thread2.join();
	//thread3.join();

	system("pause");
	return 0;
}


void update_settings(string path, bool is_print_map)
{
	ifstream in(path); // окрываем xml файл настроек для чтения
	string line;
	bool saving = false;
	if (in.is_open())
	{
		while (getline(in, line))
		{
			if (line == "<data>")
			{
				// начало данных
				saving = true;

			}
			else
			{
				if (line.find("</data>") != string::npos)
				{
					//конец данных пришел
					saving = false;
				}
				else
				{
					if (saving)
					{
						int first_l_arrow = line.find_first_of("<");
						int first_r_arrow = line.find_first_of(">");
						int last_l_arrow = line.find("</");

						string key = line.substr(first_l_arrow + 1, first_r_arrow - first_l_arrow - 1);
						string value = line.substr(first_r_arrow + 1, last_l_arrow - first_r_arrow - 1);

						if (key != "")
							settings[key] = value;
						else
							cout << " -- ERROR parsing XML. key is empty." << endl;
					}
				}
			}
		}
	}
	in.close();
	if (saving == true)
	{
		cout << " -- ERROR parsing XML. not founded end of data block." << endl;
	}

	if (is_print_map)
	{
		cout << "--- printing settings map ---" << endl;
		// printing settings map
		for (auto elem : settings)
		{
			cout << elem.first << "___" << elem.second << "___" << endl;
		}
	}
}

int capture_cam(stream_info *info)
{
	string full_path_for_saving_video = info->path_to_saving_video + to_string(info->stream_descr) + ".avi";
	string log_file_full_path = log_directory + to_string(info->stream_descr) + ".txt";
	log(log_file_full_path, "This is " + full_path_for_saving_video + " from cam " + info->path_to_cam + "\n");
	log(log_file_full_path, "Try to connect camera ...\n", true);

	VideoCapture cap(info->path_to_cam);
	if (!cap.isOpened())
	{
		log(log_file_full_path, "Cannot connect to camera\n", true);
		getchar();
		return -1;
	}
	log(log_file_full_path, "Camera connected!\n", true);
	
	namedWindow(full_path_for_saving_video, WINDOW_NORMAL);
	int window_size = 300;
	resizeWindow(full_path_for_saving_video, window_size, window_size);
	moveWindow(full_path_for_saving_video, (info->stream_descr - 1) * ((int)(window_size*1.1)), 0);
	
	Size frameSize(static_cast<int>(cap.get(CV_CAP_PROP_FRAME_WIDTH)), static_cast<int>(cap.get(CV_CAP_PROP_FRAME_HEIGHT)));

	VideoWriter oVideoWriter(full_path_for_saving_video, CV_FOURCC('P', 'I', 'M', '1'), info->fps, frameSize, true);
	
	if (!oVideoWriter.isOpened())
	{
		log(log_file_full_path, "ERROR: Failed to write the video\n", true);
		return -1;
	}

	int skiped_frames_saving = 0;
	int skiped_frames_classify = 0;
	int img_counter = 0;
	while (true)
	{
		Mat frame;

		bool bSuccess = cap.read(frame); // read a new frame from video

		if (!bSuccess) //if not success, break loop
		{
			log(log_file_full_path, "ERROR: Cannot read a frame from video file\n", true);
			destroyWindow(full_path_for_saving_video);
			break;
		}

		if (skiped_frames_saving++ == info->skip_frames_saving)
		{
			oVideoWriter.write(frame); //writer the frame into the file
			skiped_frames_saving = 0;
		}

		if (skiped_frames_classify++ == info->skip_frames_classify)
		{
			string full_path_for_saving_img = info->path_to_saving_imgs + to_string(info->stream_descr) + "_" + to_string(img_counter++) + ".jpg";
			imwrite(full_path_for_saving_img, frame);
			skiped_frames_classify = 0;
		}

		if(info->is_show_on_screen)
			imshow(full_path_for_saving_video, frame);

		if (waitKey(10) == 27)
		{
			log(log_file_full_path, "Esc key is pressed by user\n", true);
			destroyWindow(full_path_for_saving_video);
			break;
		}
	}
}

void log(string full_file_path, string message, bool is_cout)
{
	ofstream fout(full_file_path, ios_base::app);
	fout << message;
	fout.close();

	if (is_cout)
		cout << message;
}