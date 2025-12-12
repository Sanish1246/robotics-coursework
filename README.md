# Getting started

## About this project

This project is desgned to work with the [Yahboom 6 DOF Dofbot Pi](https://www.yahboom.net/study/Dofbot-Pi)

## Clone the repo

Clone the project repo in a folder of your choice by running the following command in your terminal

```
git clone https://github.com/Sanish1246/robotics-coursework.git
```

## Installing dependencies

Navigate to the cloned robotics-coursework folder

```
cd robotics-coursework
```

In order to install all dependencies for the program, run the following command:

```
pip install -r requirements.txt
```

If necessary, you may first need to create a virtual environment before installing the dependencies, by running the command

```
python -m venv venv
```

## Starting the application

First, ensure that the robotic arm is switched on.
Then, run the following command to start the Streamlit application to use the model:

```
streamlit run gui.py
```

## Accessing the application

If everything has been done correctly, the application should be available at this url

```
http://localhost:8501
```

# How to use

## Searching for items

You can click on any item to add them to the search queue.
Once you press on "Search", the robot, will start to scan the surrounding area to find and pick the requested items.

## Eergency stop

At any time during operation, you may click on the "Emergency stop" button to halt the robot's operations and make it return to its original position, hence erasing the search queue.
