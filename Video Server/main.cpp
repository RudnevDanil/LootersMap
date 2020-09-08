#include <opencv2/highgui.hpp>
//#include <windows.h>
#include <iostream>
#include <fstream>
#include <string>
#include <thread>
#include <map>
#include <ctime>

using namespace cv;
using namespace std;

string log_directory = "./log/";
map <string, string> settings;

// Êîíòðîëèðóåò ÷òîáû äåñêðèòîðû íå ïåðåñåêàëèñü.
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

// Îáîáùåíèå èíôîðìàöèè ïî ïîòîêó âèäåîçàõâàòà. Õðàíèò âñåâîçìîæíîûå íàñòðîéêè, êàñàþùèåñÿ êàæäîãî ïîòîêà.
class stream_info
{
public:
    string path_to_cam;			// VideoCapture rstp link
    string path_to_saving_video;// where to save avi
    string path_to_saving_imgs;	// where to save frames
    int skip_frames_saving;		// amount skipped frames while recording avi. -1 for not saving
    int skip_frames_classify;	// amount skipped frames in saving imgs. Recorded imgs will be classifyed. -1 for not classify
    int fps;					// fps in recorded video
    int stream_descr;			// individual descriptor of the stream
    bool is_show_on_screen;		// will online video be shown on the screen
    int frames_in_one_avi_file; // max size of avi measured in frames

    stream_info(string path_to_cam, int fps, int skip_frames_saving, int skip_frames_classify, string path_to_saving_video, string path_to_saving_imgs, int stream_descr, bool is_show_on_screen, int frames_in_one_avi_file)
    {
        this->path_to_cam = path_to_cam;
        this->fps = fps;
        this->path_to_saving_video = path_to_saving_video;
        this->path_to_saving_imgs = path_to_saving_imgs;
        this->skip_frames_saving = skip_frames_saving;
        this->skip_frames_classify = skip_frames_classify;
        this->stream_descr = stream_descr;
        this->is_show_on_screen = is_show_on_screen;
        this->frames_in_one_avi_file = frames_in_one_avi_file;
    }
};

// Îáíîâëåíèå íàñòðîåê settings èç xml ôàéëà
void update_settings(string path, bool is_print_map);

// Çàõâàò âèäåî, îòäåëåíèå èçîáðàæåíèé(ðåàëèçîâàòü) è çàïðîñ êëàññèôèêàöèè(ðåàëèçîâàòü)
int capture_cam(stream_info *info);

// Ëîãèðîâàíèå èíôîðìàöèè â ñîîòâåòñòâóþùåì ïîòîêó ôàéëå
void log(string full_file_path, string message, bool is_cout = false);

int main()
{
    // remove files from log and saved_imgs directories
    system("rm -rf ./log/*");
    system("rm -rf ./saved_imgs/*");


    // ÷òåíèå ìàññèâà íàñòðîåê
    cout << "update_settings" << endl;
    update_settings("./xml/settings.xml", true);
    cout << "update_settings DONE" << endl << endl;

    // Capture video
    cout << endl << endl << "capture ..." << endl;
    string path_to_saving_video = "./saved_video/";
    string path_to_saving_imgs = "./saved_imgs/";
    individual_descriptor descriptors;

    // make streams
    stream_info *stream_1 = new stream_info("rtsp://admin:admin@192.168.144.200:554/snl/live/1/1", 25, 0, 50, path_to_saving_video, path_to_saving_imgs, descriptors.next(), true,10*25);
    //stream_info *stream_2 = new stream_info("rtsp://admin:admin@192.168.144.200:554/snl/live/1/1", 25, 25, 25, path_to_saving_video, path_to_saving_imgs, descriptors.next(), true,100);
    //stream_info *stream_3 = new stream_info("rtsp://admin:admin@192.168.144.200:554/snl/live/1/1", 25, 25, 25, path_to_saving_video, path_to_saving_imgs, descriptors.next(), true,100);

    // start threads
    thread thread1(capture_cam, stream_1);
    //thread thread2(capture_cam, stream_2);
    //thread thread3(capture_cam, stream_3);



    // witing threads
    thread1.join();
    //thread2.join();
    //thread3.join();


    return 0;
}


void update_settings(string path, bool is_print_map)
{
    ifstream in(path); // îêðûâàåì xml ôàéë íàñòðîåê äëÿ ÷òåíèÿ
    string line;
    bool saving = false;
    if (in.is_open())
    {
        while (getline(in, line))
        {
            if (line.find("<data>") != string::npos)
            {
                cout << "start data \n";
                saving = true;

            }
            else
            {
                if (line.find("</data>") != string::npos)
                {
                    cout << "end data \n";
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

    int avi_file_counter = 0;
    int frames_recorded = 0;
    string curent_avi_path = full_path_for_saving_video;
    time_t st_recording_date = time(0); // now time
    struct tm *now = localtime(&st_recording_date);
    string date_formated = to_string(now->tm_year + 1900) + "_" + to_string(now->tm_mon + 1) + "_" + to_string(now->tm_mday) + "__" + to_string(now->tm_hour) + ":" + to_string(now->tm_min) + ":" + to_string(now->tm_sec);
    curent_avi_path.insert(full_path_for_saving_video.length()-4,"__" + date_formated + "__" + to_string(avi_file_counter));
    VideoWriter *oVideoWriter = new VideoWriter(curent_avi_path, CV_FOURCC('P', 'I', 'M', '1'), info->fps, frameSize, true);

    if (!oVideoWriter->isOpened())
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
            if (frames_recorded >= info->frames_in_one_avi_file)
            {
                curent_avi_path = full_path_for_saving_video;
                st_recording_date = time(0); // now time
                now = localtime(&st_recording_date);
                string date_formated = to_string(now->tm_year + 1900) + "_" + to_string(now->tm_mon + 1) + "_" + to_string(now->tm_mday) + "__" + to_string(now->tm_hour) + ":" + to_string(now->tm_min) + ":" + to_string(now->tm_sec);
                curent_avi_path.insert(full_path_for_saving_video.length()-4,"__" + date_formated + "__" + to_string(++avi_file_counter));
                oVideoWriter = new VideoWriter(curent_avi_path, CV_FOURCC('P', 'I', 'M', '1'), info->fps, frameSize, true);
                frames_recorded = 0;
            }
            oVideoWriter->write(frame); //writer the frame into the file
            frames_recorded++;
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
    return 0;
}

void log(string full_file_path, string message, bool is_cout)
{
    ofstream fout(full_file_path, ios_base::app);
    fout << message;
    fout.close();

    if (is_cout)
        cout << message;
}
