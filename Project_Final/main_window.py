from PySide2.QtCore import QTimer, Qt, QEvent
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QRadioButton, QMessageBox, QListView, QFileDialog, QProgressDialog

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from scipy.integrate import odeint

import differential
from app_settings import AppSettings
from differential import Ball
from bodies_model import BodiesModel
import os
import json

from editor_dialog import EditorDialog
from settings_dialog import SettingsDialog

# Easter egg!
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


class BodyLines:  # Stores the matplotlib lines on the graph. This keeps track of them for the animation.
    def __init__(self, trail_lines, ball_lines):
        self.trail_lines = trail_lines
        self.ball_lines = ball_lines


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)  # Starting to initialise the widget.

        # SETTING VALS TO BE USED FOR FUNCTIONS ######################################
        self.ball_n_position = None
        self.is_current_data_3d = True  # Is it 3D? We want to know if we want to draw in 3d or 2d regardless of radio button.
        self.app_settings = AppSettings()
        self.total_time = None
        self.current_plot = None

        self.min_extent = -1.0
        self.max_extent = 1.0
        self.zoom_multiplier = 1.0
        ##############################################################################

        self.body_storage = BodiesModel()  # List of bodies and when bodies change, update in UI too!

        # ADJUST LAST ARRAY ELEMENT TO ADJUST AMOUNT OF SAMPLES, IMPORTANT FOR CLOSE ENCOUNTERS.
        self.total_time = np.linspace(0, self.app_settings.max_time, self.app_settings.time_samples)

        # Horizontal panel created
        h_layout = QHBoxLayout()
        self.setLayout(h_layout)

        canvas_container_widget = QWidget(self)  # Widget that contains canvas and toolbar
        canvas_v_layout = QVBoxLayout()  # Creates the box layout
        canvas_container_widget.setLayout(canvas_v_layout)
        h_layout.addWidget(canvas_container_widget)  # Adds the container on top of the horizontal widget.

        self.fig = Figure()  # Create figure
        self.line_data = []
        self.canvas = FigureCanvas(self.fig)  # Canvas to display fig
        self.canvas.setSizePolicy(QSizePolicy(  # Take up as much space as possible JUST for canvas.
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        ))
        self.canvas.installEventFilter(self)
        canvas_v_layout.addWidget(self.canvas)  # Adds the canvas to the window.

        toolbar = NavigationToolbar(self.canvas, self)  # This should add a toolbar.
        canvas_v_layout.addWidget(toolbar)

        # Vertical panel created for the buttons.
        options_widget = QWidget(self)  # Widget created
        v_layout = QVBoxLayout()  # Created vertical
        options_widget.setLayout(v_layout)  # Creates the sidebar
        h_layout.addWidget(options_widget)  # Adds vertical onto horizontal one

        # USE V_LAYOUT FOR ALL ADDITIONAL ADDONS.
        gen_graph_button = QPushButton(self)  # Creating a button!
        gen_graph_button.setText("Simulate Problem")  # Button text
        gen_graph_button.clicked.connect(self.gen_plot)  # Once button clicked
        v_layout.addWidget(gen_graph_button)  # Adds the button, same for the rest addWidget

        anim_button = QPushButton(self)  # Creating a button
        anim_button.setText("Animate Current Problem")  # Set text
        anim_button.clicked.connect(self.start_plot_anim)  # When clicked
        v_layout.addWidget(anim_button)

        dimension_change_label = QLabel(self)  # Label for identification
        dimension_change_label.setText("Num of dimensions")  # Set text
        v_layout.addWidget(dimension_change_label)

        dimension_change_2d = QRadioButton(self)  # Creating radio button 2D.
        dimension_change_2d.setText("2D")
        v_layout.addWidget(dimension_change_2d)

        self.dimension_change_3d = QRadioButton(self)  # Creating radio button 3D.
        self.dimension_change_3d.setText("3D")
        self.dimension_change_3d.setChecked(True)  # By default the graph will be 3D.
        v_layout.addWidget(self.dimension_change_3d)

        self.body_list_view = QListView(self)  # This creates a list that shows all of the bodies and their colors!
        self.body_list_view.setModel(self.body_storage)  # What balls to use
        self.body_list_view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)  # Takes as much vertical space.
        v_layout.addWidget(self.body_list_view)

        #################################################
        ##### THESE BUTTONS ARE FOR BODY EDITING ########
        remove_body_button = QPushButton(self)  # Creating a button!
        remove_body_button.setText("Delete selected body")  # Button text
        remove_body_button.clicked.connect(self.remove_selected_body)  # Once button clicked
        v_layout.addWidget(remove_body_button)

        add_body_button = QPushButton(self)  # Creating a button!
        add_body_button.setText("Add body")  # Button text
        add_body_button.clicked.connect(self.add_body)  # Once button clicked
        v_layout.addWidget(add_body_button)

        edit_body_button = QPushButton(self)  # Creating a button!
        edit_body_button.setText("Edit body")  # Button text
        edit_body_button.clicked.connect(self.edit_body)  # Once button clicked
        v_layout.addWidget(edit_body_button)  # This is to edit a ball.

        #################################################
        # SAVE, LOAD, AND EDIT SETTINGS
        save_button = QPushButton(self)  # Creating a button!
        save_button.setText("Save")  # Button text
        save_button.clicked.connect(self.save)  # Once button clicked
        v_layout.addWidget(save_button)  # This is to save the current config

        load_button = QPushButton(self)  # Creating a button!
        load_button.setText("Load")  # Button text
        load_button.clicked.connect(self.load)  # Once button clicked
        v_layout.addWidget(load_button)  # This is to load a b

        edit_settings_button = QPushButton(self)  # Creating a button!
        edit_settings_button.setText("Settings")  # Button text
        edit_settings_button.clicked.connect(self.edit_settings)  # Once button clicked
        v_layout.addWidget(edit_settings_button)  # This is to edit a ball.
        #################################################

        self.time_elapsed_label = QLabel(self)  # This label will show the time elapsed when animating.
        v_layout.addWidget(self.time_elapsed_label)

        self.setWindowTitle('N-Body figurator')  # Sets title

        self.time_samples_to_draw = 0  # How many rows of the array we want to draw

        self.redraw_timer = QTimer(self)  # Creates timer
        self.redraw_timer.setInterval(1000 / 30)  # 30 frames per second animation.
        self.redraw_timer.timeout.connect(self.redraw_plot)  # When timer times out, call redraw plot function

    def get_num_dimensions(self):  # Sets dimension to view in
        if self.is_current_data_3d:  # Same as a boolean, defaults to is it true?
            return 3
        else:
            return 2

    def remove_selected_body(self):
        if self.body_list_view.selectionModel().hasSelection():  # If you select the body on the panel.
            to_remove = self.body_list_view.selectionModel().selectedRows()[0].row()  # wish to remove this row
            self.body_storage.remove_at(to_remove)  # Remove at this

    def add_body(self):
        new_body = Ball("New body!")  # Default text for new body
        dialog = EditorDialog(new_body)  # begin dialog
        dialog.exec_()

        self.body_storage.append(new_body)  # Put into body storage.

    def edit_body(self):  # This function will allow the editing of currently existing balls.
        if self.body_list_view.selectionModel().hasSelection():  # If you select the body on the panel.
            index = self.body_list_view.selectionModel().selectedRows()[0].row()  # Figure out selected row.

            dialog = EditorDialog(self.body_storage[index])  # Put in.
            dialog.exec_()

            self.body_storage.on_body_changed(index)  # Calls function to inform UI might need to change what is shown.

    def edit_settings(self):  # Executes the setting button.
        dialog = SettingsDialog(self.app_settings)
        dialog.exec_()

    def gen_plot(self):
        if len(self.body_storage) == 0:
            pixmap = QPixmap()
            pixmap.load(os.path.join(SCRIPT_DIR, "easteregg", "easteregg.png"))  # What is this?

            message_box = QMessageBox()  # Easter Egg :)
            message_box.setWindowTitle("Oh noes!")
            message_box.setText("You have no bodies to simulate!")
            message_box.setInformativeText("Honestly, what did you expect by simulating nothing?")
            message_box.setIconPixmap(pixmap)
            message_box.exec_()
            return

        # Creating a progress bar to see how much of the tasks are done.
        prog_dialog = QProgressDialog("Simulating...", None, 0, 100, self)
        prog_dialog.setWindowModality(Qt.WindowModal)  # Cannot interact with window behind.
        prog_dialog.show()

        self.line_data = []
        self.zoom_multiplier = 1.0  # For the graph, reset graph zoom.

        #######################################################################
        # CONSTANTS
        G = 6.67408e-11
        number_dimensions = 2
        if self.dimension_change_3d.isChecked():
            number_dimensions = 3

        self.is_current_data_3d = number_dimensions == 3

        #######################################################################

        # ADJUST LAST ARRAY ELEMENT TO ADJUST AMOUNT OF SAMPLES, IMPORTANT FOR CLOSE ENCOUNTERS.
        self.total_time = np.linspace(0, self.app_settings.max_time, self.app_settings.time_samples)

        for body in self.body_storage:
            body.clear_results(number_dimensions)  # Sets number dimensions once all of the arrays have been set.

        body_storage_length = len(self.body_storage)  # Gets body storage length.

        n_bodies = body_storage_length  # Useful in below. For now this is 3. Keep body storage len because readability.

        # AUTO-INITIAL CONDITION FITTER
        if number_dimensions == 2:  # If 2D

            # Body storage length is x2 to account for velocity as well.
            size_initial_conditions = np.zeros(
                [body_storage_length * 2, number_dimensions])  # Sets how long the n_body maker will be.

            size_index = 0  # To be used for importing all ball data.
            while size_index < n_bodies:  # Also figures out the number of dimensions.
                size_initial_conditions[size_index, :] = self.body_storage[size_index].pos_vector
                size_initial_conditions[size_index + n_bodies, :] = self.body_storage[
                    size_index].vel_vector  # Dynamically uses the amount of n_bodies to find an appropriate initial parameter.
                size_index += 1  # So it properly increments.
        elif number_dimensions == 3:  # If 3D

            # Body storage length is x2 to account for velocity as well.
            size_initial_conditions = np.zeros([body_storage_length * 2, number_dimensions])

            size_index = 0
            while size_index < n_bodies:  # Also figures out the number of dimensions.
                size_initial_conditions[size_index, :] = self.body_storage[size_index].pos_vector
                size_initial_conditions[size_index + n_bodies, :] = self.body_storage[
                    size_index].vel_vector  # Dynamically uses the amount of n_bodies to find an appropriate initial parameter.
                size_index += 1  # So it properly increments.
        else:
            raise ValueError("Bad number of dimensions")  # One dimension option coming soon!

        initial_parameters = size_initial_conditions  # This is so it is flattened later.

        size_of_parameters = np.shape(initial_parameters)
        initial_parameters = initial_parameters.flatten()  # Turns to 1D

        # Odeint go.
        solutions_1 = odeint(
            differential.newton_newODE_solver_2,
            initial_parameters,
            self.total_time,
            args=(
                G,
                size_of_parameters,
                n_bodies,
                number_dimensions,
                self.body_storage,
                prog_dialog,
                self.app_settings.max_time
            ),
            tfirst=True
        )

        # Initial array resize for each ball (ease of use).
        size_solutions_1 = int(np.size(solutions_1, axis=1))
        half_size_solutions_1 = int(size_solutions_1 / 2)

        # Splits up the position and velocity appropriately.
        self.ball_n_position = solutions_1[:, 0:half_size_solutions_1]

        # Close the progress dialog.
        prog_dialog.close()

        # Redraw everything at once.
        self.time_samples_to_draw = self.app_settings.time_samples
        self.redraw_plot()

    # Draws the plot which is either 2D or 3D.
    def redraw_plot(self):
        if self.ball_n_position is None:  # If no data, do not do anything.
            return

        # Always replot 2D graphs
        needs_replot = len(self.line_data) == 0 or not self.is_current_data_3d

        # Getting the dimensions and storage length.
        number_dimensions = self.get_num_dimensions()
        body_storage_length = len(self.body_storage)

        is_at_end = self.time_samples_to_draw == self.app_settings.time_samples  # Determines if ball reaches end

        # Each frame we want to draw x more timesteps.
        self.time_samples_to_draw += int(self.app_settings.time_samples * 0.01 * self.app_settings.anim_speed)
        self.time_samples_to_draw = min(self.time_samples_to_draw, self.app_settings.time_samples)

        if is_at_end:  # If ending animation reached, show entire trail.
            trail_begin = 0
        else:
            # Determines the length of the tail.
            trail_length_samples = min(int(self.app_settings.time_samples * 0.05), self.time_samples_to_draw - 1)
            trail_begin = self.time_samples_to_draw - trail_length_samples

        if needs_replot:  # To replot
            self.fig.clear()

        # If 2 dimensions, now draw the graph in 2D.
        if number_dimensions == 2:
            min_extent_x = 0
            max_extent_x = 0

            min_extent_y = 0
            max_extent_y = 0

            if needs_replot:
                ball_motion = self.fig.add_subplot(111)  # Replots as required.
                self.current_plot = ball_motion
            else:
                ball_motion = self.current_plot  # Reuse current plot.

            for i_ball in range(body_storage_length):
                trail_lines, = ball_motion.plot(
                    self.ball_n_position[trail_begin:self.time_samples_to_draw - 1, 0 + (i_ball * 2)],
                    self.ball_n_position[trail_begin:self.time_samples_to_draw - 1, 1 + (i_ball * 2)],
                    color=self.body_storage[i_ball].color
                )  # Selects all the balls.

                ball_lines, = ball_motion.plot(
                    self.ball_n_position[self.time_samples_to_draw - 1, 0 + (i_ball * 2)],
                    self.ball_n_position[self.time_samples_to_draw - 1, 1 + (i_ball * 2)],
                    "o",
                    color=self.body_storage[i_ball].color  # This one is for the end sphere!
                )

                self.line_data.append(BodyLines(trail_lines, ball_lines))  # Keep track of line data.

                # See if we need to expand the graph bounds
                ball_max_x = np.max(self.ball_n_position[:, 0 + (i_ball * 2)])
                ball_min_x = np.min(self.ball_n_position[:, 0 + (i_ball * 2)])
                ball_max_y = np.max(self.ball_n_position[:, 1 + (i_ball * 2)])
                ball_min_y = np.min(self.ball_n_position[:, 1 + (i_ball * 2)])

                max_extent_x = max(max_extent_x, ball_max_x)
                min_extent_x = min(min_extent_x, ball_min_x)
                max_extent_y = max(max_extent_y, ball_max_y)
                min_extent_y = min(min_extent_y, ball_min_y)

            # Kinda ugly hack to prevent it scaling during animation for 2D
            ball_motion.plot(
                min_extent_x - (abs(min_extent_x * 0.2)),
                min_extent_y - (abs(min_extent_y * 0.2)),
                color=(0.0, 0.0, 0.0, 0.0)
            )
            ball_motion.plot(
                max_extent_x + (abs(max_extent_x * 0.2)),
                max_extent_y + (abs(max_extent_y * 0.2)),
                color=(0.0, 0.0, 0.0, 0.0)
            )

            # Set labels
            ball_motion.set_xlabel("x distance")
            ball_motion.set_ylabel("y distance")
            ball_motion.axis("equal")

        # The 3D case now.
        elif number_dimensions == 3:
            min_extent = 0
            max_extent = 0

            if needs_replot:
                ball_motion = self.fig.add_subplot(111, projection="3d")
                self.current_plot = ball_motion  # Replots if needed.
            else:
                ball_motion = self.current_plot

            for i_ball in range(body_storage_length):  # Takes over entire i_ball range.

                # For the trail
                trail_x_data = self.ball_n_position[trail_begin:self.time_samples_to_draw - 1, 0 + (i_ball * 3)]
                trail_y_data = self.ball_n_position[trail_begin:self.time_samples_to_draw - 1, 1 + (i_ball * 3)]
                trail_z_data = self.ball_n_position[trail_begin:self.time_samples_to_draw - 1, 2 + (i_ball * 3)]

                # For the end ball.
                ball_x = self.ball_n_position[self.time_samples_to_draw - 1, 0 + (i_ball * 3)]
                ball_y = self.ball_n_position[self.time_samples_to_draw - 1, 1 + (i_ball * 3)]
                ball_z = self.ball_n_position[self.time_samples_to_draw - 1, 2 + (i_ball * 3)]

                # Figure if we need to replot data or update existing line data.
                if needs_replot:
                    trail_lines, = ball_motion.plot3D(
                        trail_x_data,
                        trail_y_data,
                        trail_z_data,
                        color=self.body_storage[i_ball].color
                    )  # Selects all the balls.

                    ball_lines, = ball_motion.plot3D(
                        ball_x,
                        ball_y,
                        ball_z,
                        "o",
                        color=self.body_storage[i_ball].color
                    )

                    self.line_data.append(BodyLines(trail_lines, ball_lines))  # Keep track of line data for animation.

                    # See if we need to expand the graph bounds
                    ball_max_x = np.max(self.ball_n_position[:, 0 + (i_ball * 3)])
                    ball_min_x = np.min(self.ball_n_position[:, 0 + (i_ball * 3)])
                    ball_max_y = np.max(self.ball_n_position[:, 1 + (i_ball * 3)])
                    ball_min_y = np.min(self.ball_n_position[:, 1 + (i_ball * 3)])
                    ball_max_z = np.max(self.ball_n_position[:, 2 + (i_ball * 3)])
                    ball_min_z = np.min(self.ball_n_position[:, 2 + (i_ball * 3)])

                    max_extent = max(max_extent, ball_max_x)
                    min_extent = min(min_extent, ball_min_x)
                    max_extent = max(max_extent, ball_max_y)
                    min_extent = min(min_extent, ball_min_y)
                    max_extent = max(max_extent, ball_max_z)
                    min_extent = min(min_extent, ball_min_z)

                else:
                    ball_lines = self.line_data[i_ball]  # Or update existing line data.
                    ball_lines.trail_lines.set_data_3d(trail_x_data, trail_y_data, trail_z_data)
                    ball_lines.ball_lines.set_data_3d(ball_x, ball_y, ball_z)

            if needs_replot:
                ball_motion.set_xlabel("x distance")
                ball_motion.set_ylabel("y distance")
                ball_motion.set_zlabel("z distance")

                # Sets the limits for the graph dynamically.
                # We do this such that we can have a 1:1:1 scale between x y z
                ball_motion.set_xlim3d([min_extent, max_extent])
                ball_motion.set_ylim3d([min_extent, max_extent])
                ball_motion.set_zlim3d([min_extent, max_extent])

                self.fig.tight_layout()

                self.min_extent = min_extent
                self.max_extent = max_extent

        # Draw the canvas
        self.canvas.draw()

        seconds_elapsed = self.total_time[self.time_samples_to_draw - 1]  # Record time.
        self.time_elapsed_label.setText(f"Elapsed: {prettify_elapsed_seconds(seconds_elapsed)}")  # Updates the time.

        if is_at_end:  # Once it went through all the time samples
            self.redraw_timer.stop()  # Stop animating.

    def start_plot_anim(self):  # Begins the animation.
        self.time_samples_to_draw = 0
        self.redraw_timer.start()

    def save(self):  # The function to save a body configuration
        # Saving as a json file
        file_path, file_type = QFileDialog.getSaveFileName(self, "Save config JSON", "", "JSON files (*.json)")
        if len(file_path) != 0:  # If file path provided.
            data = {
                "bodies": [body.serialize() for body in self.body_storage],  # Runs the save function.
                "settings": {
                    "time_samples": self.app_settings.time_samples,
                    "max_time": self.app_settings.max_time,
                    "anim_speed": self.app_settings.anim_speed,
                },
            }
            json_str = json.dumps(data)  # Outputs as a json.

            with open(file_path, "w") as f:
                f.write(json_str)  # Write the sets of file into the destination.

    def load(self):  # The function to load a set of bodies.
        # Gets the file path.
        file_path, file_type = QFileDialog.getOpenFileName(self, "Load config JSON", "", "JSON files (*.json)")
        if len(file_path) != 0:  # If a file path is specified.
            with open(file_path, "r") as f:
                content = f.read()  # To read the loaded contents

            data = json.loads(content)  # Loads

            self.body_storage.clear()  # Clears initial body storage.
            for body_info in data["bodies"]:
                body = Ball("")
                body.deserialize(body_info)  # Thus puts it into the program.

                self.body_storage.append(body)

            if "settings" in data:
                settings = data["settings"]
                self.app_settings.time_samples = settings["time_samples"]
                self.app_settings.max_time = settings["max_time"]
                self.app_settings.anim_speed = settings["anim_speed"]

    # This is to intercept mouse wheel event for a custom zoom in.
    # Thus our own zoom on the graph to center onto the 0,0,0 axis.
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Wheel:
            if self.current_plot is not None and self.is_current_data_3d:
                adjust = event.angleDelta().y() * 0.0005
                self.zoom_multiplier += adjust
                self.zoom_multiplier = max(self.zoom_multiplier, 0.0001)

                self.current_plot.set_xlim3d([self.min_extent * self.zoom_multiplier, self.max_extent * self.zoom_multiplier])
                self.current_plot.set_ylim3d([self.min_extent * self.zoom_multiplier, self.max_extent * self.zoom_multiplier])
                self.current_plot.set_zlim3d([self.min_extent * self.zoom_multiplier, self.max_extent * self.zoom_multiplier])

                self.canvas.draw()

            # Prevent the default behaviour
            return True

        # Don't prevent Qt from doing its default behaviour for this event, whatever this event could be.
        return False


# Makes the time a bit more understandable, and scales!
def prettify_elapsed_seconds(seconds):
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 60 * 60:
        return f"{seconds / 60:.2f} minutes"
    elif seconds < 60 * 60 * 60:
        return f"{seconds / (60 * 60):.2f} hours"
    elif seconds < 60 * 60 * 60 * 24:
        return f"{seconds / (60 * 60 * 24):.2f} days"
    else:
        return f"{seconds / (60 * 60 * 24 * 365):.2f} years"
