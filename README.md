# Nose Controled Snake Game

### Description

This is a simple computer vision project in which you use your nose to control a snake in the popular snake game. Can be
useful for people with motor disabilities.

You can move the snake up, down, left and right to catch the dot. The game ends once your snake touches the outside
limits of the game window. You then have the option to start the game again by moving your nose as specified in the
screen.

### References

This implementation takes elements from two existing projects:

1) Snake game in Pygame (controlled by keyboard): https://github.com/rajatdiptabiswas/snake-pygame
2) Eyes detection project: https://towardsdatascience.com/real-time-eye-tracking-using-opencv-and-dlib-b504ca724ac6

What is new for this implementation is:

1) Added extra features to snake game to allow for control via queue received commands
2) Established communication via queue between the nose detection service and the snake game
3) Changed eye detection code to nose detection
4) Added logic to detect nose movement variations and translate them into up,down,left,right commands

### Install

1) Run the following command

```
python setup.py install
```

Note: If you have issues installing dlib, install cmake separately and try the above step again

```
pip install cmake
pip install dlib
```

2) For the snake game and nose detection system to communicate, you will need to have a RabbitMQ broker running in your
   local machine. In order to do this, run the following:

```
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.9-management
```

Note: This requires docker to be installed in your machine.

3) Get the face detector classification model from here: https://github.com/italojs/facial-landmarks-recognition/blob/master/shape_predictor_68_face_landmarks.dat
and place it in the `computer_vision` folder.

### Run

1) In order to run detector, start by running

```
python computer_vision/nose_tracking.py
```

2) Once your camera starts, use the threshold controller and adjust the bar until you see the contour of your nose in
   green in the video camera image
3) Once you see your nose contour, run the snake game using

```
python snake_game/snake.py
```

4) The game should then start. You can move your nose to control the snake

### TODO

* Improve response time from nose detection to snake movement