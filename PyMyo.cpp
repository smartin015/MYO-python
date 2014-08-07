// Copyright (C) 2013-2014 Thalmic Labs Inc.
// Distributed under the Myo SDK license agreement. See LICENSE.txt for details.
// Modified to expose Myo data to Python
// Paul Lutz
// Scott Martin
// Fabricate.IO
#include <iostream>
#include <thread>

// Indicates the Myo is not on an arm
#define OFF_ARM 'A'
#define FIND_MYO_TIMEOUT_MS 10000
#define UPDATE_EVENT_PD_MS 50

// The only file that needs to be included to use the Myo C++ SDK is myo.hpp.
#include <myo/myo.hpp>

// Classes that inherit from myo::DeviceListener can be used to receive events from Myo devices. DeviceListener
// provides several virtual functions for handling different kinds of events. If you do not override an event, the
// default behavior is to do nothing.
class DataCollector : public myo::DeviceListener {
private:
	// These values are set by onArmRecognized() and onArmLost() above.
    bool onArm;
    myo::Arm whichArm;

    // These values are set by onOrientationData() and onPose() above.
    int roll_w, pitch_w, yaw_w;
    myo::Pose currentPose;

	//stores w, x, y, and z rotation
	float quat_arr[4];

	float accel_arr[3];
	myo::Myo* myMyo;

public:
    DataCollector()
    : onArm(false), roll_w(0), pitch_w(0), yaw_w(0), currentPose() {
		for(int i = 0;i< sizeof quat_arr;i++) {
			quat_arr[i] = 0.0;
		}
    }

	void setMyo(myo::Myo* myo) {
		myMyo = myo;
	}

    // Called whenever the Myo device provides its current orientation, which is represented
    // as a unit quaternion.
    void onOrientationData(myo::Myo* myo, uint64_t timestamp, const myo::Quaternion<float>& quat) {
		quat_arr[0] = quat.w();
		quat_arr[1] = quat.x();
		quat_arr[2] = quat.y();
		quat_arr[3] = quat.z();
    }

    // Called whenever the Myo detects that the person wearing it has changed their pose, for example,
    // making a fist, or not making a fist anymore.
    void onPose(myo::Myo* myo, uint64_t timestamp, myo::Pose pose) {
		currentPose = pose;
    }

    // Called whenever Myo has recognized a setup gesture after someone has put it on their
    // arm. This lets Myo know which arm it's on and which way it's facing.
    void onArmRecognized(myo::Myo* myo, uint64_t timestamp, myo::Arm arm, myo::XDirection xDirection) {
        onArm = true;
        whichArm = arm;
    }

    // Called whenever Myo has detected that it was moved from a stable position on a person's arm after
    // it recognized the arm. Typically this happens when someone takes Myo off of their arm, but it can also happen
    // when Myo is moved around on the arm.
    void onArmLost(myo::Myo* myo, uint64_t timestamp) {
        onArm = false;
    }

	// Called when the Myo sends acceleration data.
	void onAccelerometerData (myo::Myo* myo, uint64_t timestamp, const myo::Vector3<float> &accel) {
		accel_arr[0] = accel.x();
		accel_arr[1] = accel.y();
		accel_arr[2] = accel.z();
	}

	// Vibrates the Myo
	void vibrate(int duration) {
		switch (duration) {
			case 1:               
				myMyo->vibrate(myo::Myo::vibrationShort);
				break;
			case 2:               
				myMyo->vibrate(myo::Myo::vibrationMedium);
				break;
			case 3:               
				myMyo->vibrate(myo::Myo::vibrationLong);
				break;
		}
	}

    // Prints the current values that were updated by the on...() functions above.
    void print() {

		// Prints x, y, and z acceleration of the Myo
		for(int i = 0;i< (sizeof(accel_arr)/sizeof(*accel_arr));i++) {	
			char* bits = reinterpret_cast<char*>(&accel_arr[i]);
			for(int n = 0; n < sizeof(float); ++n) {
				std::cout << (bits[n]);
			}
		}

		// Prints w, x, y, and z rotation of the Myo
		for(int i = 0;i< (sizeof(quat_arr)/sizeof(*quat_arr));i++) {
			char* bits = reinterpret_cast<char*>(&quat_arr[i]);
			for(int n = 0; n < sizeof(float); ++n) {
				std::cout << (bits[n]);
			}
		}

		// Prints Pose byte
		unsigned char poseByte;
		poseByte = currentPose.type() & 0xFF;
		std::cout << poseByte;

		// Prints which arm the Myo is on: 0 = right, 1 = left
		if(onArm) {
			std::cout << (unsigned char)whichArm;
		} else {
			std::cout << OFF_ARM;
		}

        std::cout << '\n';
        std::cout << std::flush;
    }


};


bool collectorInputBool;
std::string input;
DataCollector collector;

void inputThread()
{
	collectorInputBool = false;
	while(true)
	{
		std::cin >> input;
		if(std::cin.fail())
		{
			std::exit(0);
		}

		collectorInputBool = true;
		if(&collector != NULL)
		{
			switch (input[0])
			{
				case 'a':               
					collector.vibrate(1);
					break;
				case 'b':               
					collector.vibrate(2);
					break;
				case 'c':               
					collector.vibrate(3);
					break;
				default:
					collector.vibrate(2);
					collector.vibrate(2); 
					collector.vibrate(2);
					break;
			}
		}
		else
		{
			std::cout << "null collector!";
		}
		collectorInputBool = false;
	}
}

int main(int argc, char** argv)
{
    try {

		collectorInputBool = false;
		
		myo::Hub hub("com.fabricate.pyo"); // This provides access to one or more Myos.

		myo::Myo* myo = hub.waitForMyo(FIND_MYO_TIMEOUT_MS);
		if (!myo) {
			throw std::runtime_error("Unable to find a Myo!");
		}
		collector.setMyo(myo);
		hub.addListener(&collector); // Tell the hub to send data events to the collector

		// This thread reads vibration commands
		std::thread t1 (inputThread);
		t1.detach();

		while (true) {
			if(!collectorInputBool)
			{
				hub.run(UPDATE_EVENT_PD_MS); // Allow myo to push events at the given rate
				collector.print();
			}
		}
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}