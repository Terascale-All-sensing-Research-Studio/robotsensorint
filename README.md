# Installation Process

Clone the repository using: git clone https://github.com/Terascale-All-sensing-Research-Studio/robotsensorint-Demo.git
-Required Python version: 3.8.10

# Virtual Environment
Create the virtual environment with:
- python -m venv myenv (or any other name)
- Activate it with: .\myenv\Scripts\activate
- Download the required dependecies: "pip install -r requirements.txt"
- run: python -m pip install <whl relative fullpath name>.whl

# Run the code
- cd Python
- python Robotic_demo.py


# Changes to the code
You might have to change the code if the table you use is a different height and the location where the robot goes does not match

- I use start_position() (line 179) to move the robot to where the popcorn is, if you have to change that you would change line 184
- I use end_example() (line 229) to move the robot to its end position where it hands the user the popcorn, if you have to change that you would change line 236

In order to change where you want the robot to go you use waypoints. To find the specfic waypoints you want, you would move the robot with the xbox controller to the desired position.
Then you would go to 192.168.1.10 which brings you to the Kinova web application, if you scroll all the way down you find the end effector which shows the x y z thetax thetay thetaz for your specific position
You would copy those values into the waypoint definition in the same order as it is shown.




