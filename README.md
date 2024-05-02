# Project: N-Body simulation
## Creating the venv
This is how you create a venv, activate the venv and install the dependencies, type this in the console (powershell)...
```
python -m venv venv
source ./venv/bin/activate (or venv\Scripts\activate.ps1 ?)
cd Project_Final
pip3 install -r requirements.txt
```

And then to run it while still in the venv...
```
python main.py
```

## Loading an n-body preset
Open the program for the N-body simulator.
Press the load button.
Select a JSON file in the saves folder.
Click on simulate problem FIRST, important step.
Now you can click on animate problem.

## Additional remarks
Simulations usually take between 5 seconds - 2 minutes to do that are provided in the saves.
Vectorized operations were tried as much as it could, but after a certain point they oddly decreased performance.

Inspiration for some of the code taken from this article:
https://towardsdatascience.com/modelling-the-three-body-problem-in-classical-mechanics-using-python-9dc270ad7767

One last thing, this requires pyside2 to run Qt. If you do the venv instructions, it should auto-install.
There were problems last time this package was installed, simply email if it arises.

## 2023 Remark
This project was produced October 2021. The main purpose of this project was to complete an assigned task and fulfill certain criteria that would allow for the careful study of a celestial system with an N amount of bodies. This project was developed while studying at the University of Northampton.

If you wish for the report that was produced while utilising this software, please send me a private email.

MIT License
