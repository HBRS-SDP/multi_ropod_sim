#include <ros/ros.h>
#include <image_transport/image_transport.h>
#include <opencv2/highgui/highgui.hpp>
#include <cv_bridge/cv_bridge.h>
#include <sstream> // for converting the command line parameter to integer

int main(int argc, char** argv)
{
    ros::init(argc, argv, "image_publisher");
    ros::NodeHandle nh;
    image_transport::ImageTransport it(nh);
    image_transport::Publisher pub = it.advertise("/ropod/camera/front", 1);

    double frequency;
    nh.param<double>("frequency", frequency, 20);
    ROS_DEBUG("Frequency set to %0.1f Hz", frequency);

    int device_id;
    nh.param<int>("device_id", device_id, 0);
    ROS_DEBUG("Device id set to %d ", device_id);


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
            pub.publish(msg);
            cv::waitKey(1);
        }

        ros::spinOnce();
        loop_rate.sleep();
    }
}