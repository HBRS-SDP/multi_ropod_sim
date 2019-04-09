#include <ros/ros.h>
#include <vector>
#include <image_transport/image_transport.h>
#include <opencv2/highgui/highgui.hpp>
#include <cv_bridge/cv_bridge.h>
#include <sstream> // for converting the command line parameter to integer

int main(int argc, char** argv)
{
    ros::init(argc, argv, "image_publisher");
    ros::NodeHandle nh;
    image_transport::ImageTransport it(nh);
    image_transport::Publisher camera_img_pub = it.advertise("/ropod/camera/front", 1);

    ros::Publisher camera_info_pub = nh.advertise<sensor_msgs::CameraInfo>("/ropod/camera/front/info", 1);
    sensor_msgs::CameraInfo ropod_camera_front_info;
    ropod_camera_front_info.D = {0,0,0,0,0};

    double frequency;
    nh.param<double>("/camera_driver_node/frequency", frequency, 20);
    ROS_INFO("Frequency set to %0.1f Hz", frequency);

    int device_id;
    nh.param<int>("/camera_driver_node/device_id", device_id, 0);
    ROS_INFO("Device id set to %d ", device_id);

    std::vector<double> camera_matrix;
    nh.getParam("/camera_driver_node/camera_matrix/data", camera_matrix);
    std::copy(camera_matrix.begin(), camera_matrix.end(), ropod_camera_front_info.K.begin());

    std::vector<double> distortion_coefficients;
    nh.getParam("/camera_driver_node/distortion_coefficients/data", distortion_coefficients);
    std::copy(distortion_coefficients.begin(), distortion_coefficients.end(), ropod_camera_front_info.D.begin());

    double avg_reprojection_error;
    nh.getParam("/camera_driver_node/avg_reprojection_error", avg_reprojection_error);
    
    cv::VideoCapture cap(device_id);
    // Check if video device can be opened with the given index
    if (!cap.isOpened()) return 1;
    cv::Mat frame;
    sensor_msgs::ImagePtr msg;

    ros::Rate loop_rate(20);
    while (nh.ok()) 
    {
        cap >> frame;
        // Check if grabbed frame is actually full with some content
        if (!frame.empty()) 
        {
            msg = cv_bridge::CvImage(std_msgs::Header(), "bgr8", frame).toImageMsg();
            camera_img_pub.publish(msg);

            camera_info_pub.publish(ropod_camera_front_info);
            cv::waitKey(1);
        }
        ros::spinOnce();
        loop_rate.sleep();
    }
}