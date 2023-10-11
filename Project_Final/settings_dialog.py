from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QPushButton, QFormLayout, QVBoxLayout, QWidget, QLabel, QLineEdit, QColorDialog
import math


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):  # Creating another window...
        super().__init__(parent)

        self.settings = settings  # We modify settings instead.

        v_layout = QVBoxLayout()  # The vertical layout
        self.setLayout(v_layout)

        form_widget = QWidget(self)
        self.form_layout = QFormLayout()
        form_widget.setLayout(self.form_layout)  # Sets the layout
        v_layout.addWidget(form_widget)  # Makes sure the text boxes are added.

        # Sets the text for the settings textboxes.
        self.time_samples_edit = self.make_number_edit("# of time samples", "time_samples", "%d")
        self.max_time_edit = self.make_number_edit("Max time", "max_time", "%.9f")
        self.anim_speed_edit = self.make_number_edit("Animation speed", "anim_speed", "%.9f")

        ok_button = QPushButton(self)  # The ok button.
        ok_button.setText("Ok")
        ok_button.clicked.connect(self.confirm)
        v_layout.addWidget(ok_button)  # ok... again

    # Makes a label for what we want to edit, and a textbox containing default value.
    def make_number_edit(self, text, attribute_name, format_str):
        default_value = getattr(self.settings, attribute_name)  # Gets property from object by its name. Magic.

        label = QLabel(self)  # Makes the label
        label.setText(f"{text} ({default_value:.2e})")  # Sets the text
        label.setMinimumWidth(200)

        line_edit = QLineEdit(self)  # Makes the textbox
        line_edit.setMinimumWidth(400)  # To help with precision as it converts from float -> string -> float
        line_edit.setAlignment(Qt.AlignRight)
        # Sets the default text. getattr lets us get a variable name by specifying a string, and it will find it.
        line_edit.setText(format_str % default_value)

        self.form_layout.addRow(label, line_edit)  # Formats the text boxes onto the correct positions.

        def eval_line_edit():  # This will allow us to do some fancy maths with the mass and velocity EG 4e10, 4e9*10*20
            try:
                value = eval(line_edit.text())  # Get the text in dialog box
                if type(value) == int or type(value) == float:  # Check if what user entered is evaluated to number
                    line_edit.setText(format_str % float(value))  # Do fancy math.
                    label.setText(f"{text} ({value:.2e})")  # Adds scientific notation for easier read
                else:
                    line_edit.setText(format_str % default_value)  # Else reset back to default values
                    label.setText(f"{text} ({default_value:.2e})")

            except:
                # If there was an error evaluating, reset it to default
                line_edit.setText(format_str % default_value)
                label.setText(f"{text} ({default_value:.2e})")

        line_edit.editingFinished.connect(eval_line_edit)  # When finish editing textbox, try to evaluate as maths.

        return line_edit

    def confirm(self):  # This will update all the values on the ball
        self.settings.time_samples = int(self.time_samples_edit.text())
        self.settings.max_time = float(self.max_time_edit.text())
        self.settings.anim_speed = float(self.anim_speed_edit.text())

        self.close()
