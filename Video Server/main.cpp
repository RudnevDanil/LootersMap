#include <opencv2/highgui.hpp>
//#include <windows.h>
#include <iostream>
#include <fstream>
#include <string>
#include <thread>
#include <map>
#include <ctime>

#include <unistd.h>//linux sleep

using namespace cv;
using namespace std;

string log_directory = "./log/";
string xml_directory = "./xml/";
string xml_settings = "settings.xml";
string path_to_saving_video = "./saved_video/";
string path_to_saving_imgs = "./saved_imgs/";
map <string, map<string,string>> settings;

// Descriptor class. Use it for give diferent descriptors for each stream.
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

// Stream info class. Filled by full information about stream.
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

    void log_stream_settings(string full_file_path)
    {
        ofstream fout(full_file_path, ios_base::app);
        fout << "path_to_cam = " << path_to_cam << endl;
        fout << "fps = " << fps << endl;
        fout << "path_to_saving_video = " << path_to_saving_video << endl;
        fout << "path_to_saving_imgs = " << path_to_saving_imgs << endl;
        fout << "skip_frames_saving = " << skip_frames_saving << endl;
        fout << "skip_frames_classify = " << skip_frames_classify << endl;
        fout << "stream_descr = " << stream_descr << endl;
        fout << "is_show_on_screen = " << is_show_on_screen << endl;
        fout << "frames_in_one_avi_file = " << frames_in_one_avi_file << endl;
        fout.close();
    }
};

// Reading xml settings file. (!) need to add restarting streams.
void update_settings(string path, bool is_print_map);

// Capture stream and save imgs and videos.
int capture_cam(stream_info *info);

// log message to a log file and maybe to console
void log(string full_file_path, string message, bool is_cout = false);

int main()
{

    // remove files from log and saved_imgs directories
    system((string("rm -rf ") + log_directory + string("*")).c_str());
    system((string("rm -rf ") + path_to_saving_imgs + string("*")).c_str());
    system((string("rm -rf ") + path_to_saving_video + string("*")).c_str());

    // update settings
    update_settings(xml_directory + xml_settings, true);

    // Capture video
    cout << endl << endl << "capture ..." << endl;  

    // make streams
    individual_descriptor descriptors;
    vector<stream_info*> streams_info;
    vector<thread*> threads;

    int numb_streams = stoi(settings["others"]["number_active_streams"]);
    for(int i = 0; i < numb_streams; i++)
    {
        string stream_name = "stream_" + to_string(i+1);
        streams_info.push_back(new stream_info(
                                               settings[stream_name]["path_to_cam"],
                                               stoi(settings[stream_name]["fps"]),
                                               stoi(settings[stream_name]["skip_frames_saving"]),
                                               stoi(settings[stream_name]["skip_frames_classify"]),
                                               path_to_saving_video, path_to_saving_imgs, descriptors.next(),
                                               ((settings[stream_name]["is_show_on_screen"] == "true")?true:false),
                                                stoi(settings[stream_name]["frames_in_one_avi_file"])
                                                ));

        threads.push_back(new thread(capture_cam, streams_info[i]));
        sleep(5);
    }

    // waiting threads
    for(int i = 0; i < numb_streams; i++)
    {
        threads[i]->join();
    }

    return 0;
}


void update_settings(string path, bool is_print_map)
{
    cout << "update_settings" << endl << endl;
    ifstream in(path);
    string line;
    bool saving = false;

    if (in.is_open())
    {
        map<string,string> others;
        map<string,string> cur_stream;
        bool cur_stream_state = false;
        string cur_stream_name = "";

        while (getline(in, line))
        {
            if (line == "\r")
                continue;

            if (line.find("<data>") != string::npos)
            {
                saving = true;

            }
            else
            {
                if (line.find("</data>") != string::npos)
                {
                    saving = false;
                }
                else
                {
                    if (saving)
                    {
                        int first_l_arrow = line.find_first_of("<");
                        int first_r_arrow = line.find_first_of(">");
                        int last_l_arrow = line.find("</");

                        if(last_l_arrow == -1) // stream block start
                        {
                            if(!cur_stream_state) // block not opened
                            {
                                cur_stream_state = true;
                                cur_stream_name = line.substr(first_l_arrow + 1, first_r_arrow - first_l_arrow - 1);
                                cur_stream.clear();
                            }
                            else
                            {
                                cout << " -- ERROR parsing XML. settings block damaged. start block." << endl;
                            }
                        }
                        else if(last_l_arrow == 1) // stream block end
                        {
                            if(cur_stream_state) // block already opened
                            {
                                cur_stream_state = false;
                                settings[cur_stream_name] = cur_stream;
                                cur_stream.clear();
                            }
                            else
                            {
                                cout << " -- ERROR parsing XML. settings block damaged. end block." << endl;
                            }
                        }
                        else
                        {
                            string key = line.substr(first_l_arrow + 1, first_r_arrow - first_l_arrow - 1);
                            string value = line.substr(first_r_arrow + 1, last_l_arrow - first_r_arrow - 1);

                            if (key != "")
                            {
                                if(cur_stream_state) // record. stream block opened.
                                    cur_stream[key] = value;
                                else    // record. stream block not opened.
                                    others[key] = value;
                            }
                            else
                                cout << " -- ERROR parsing XML. key is empty." << endl;
                        }
                    }
                }
            }
        }
        settings["others"] = others;
    }
    in.close();
    if (saving == true)
    {
        cout << " -- ERROR parsing XML. not founded end of data block." << endl;
    }

    if (is_print_map)
    {
        for (auto elem1 : settings)
        {
            for (auto elem2 : elem1.second)
                cout << elem1.first << "___" << elem2.first << "___" << elem2.second << endl;
            cout << endl;
        }
    }

    cout << "update_settings DONE" << endl << endl;
}

int capture_cam(stream_info *info)
{
    info->log_stream_settings(log_directory + "settings_" + to_string(info->stream_descr) + ".txt");

    string full_path_for_saving_video = info->path_to_saving_video + to_string(info->stream_descr) + ".avi";
    string log_file_full_path = log_directory + "log_"+ to_string(info->stream_descr) + ".txt";
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

        if (!bSuccess) // if not success, break loop
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
