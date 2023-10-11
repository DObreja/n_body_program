from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QDialog, QPushButton, QFormLayout, QVBoxLayout, QWidget, QLabel, QLineEdit, QColorDialog
import math

# Convert degrees to radians for both trig cases.
def sin_deg(deg):
    return math.sin(math.radians(deg))


def cos_deg(deg):
    return math.cos(math.radians(deg))


class EditorDialog(QDialog):
    def __init__(self, body, parent=None):  # Creating another window...
        super().__init__(parent)

        self.body = body

        v_layout = QVBoxLayout()  # The vertical layout
        self.setLayout(v_layout)

        form_widget = QWidget(self)  # Container for more widgets.
        self.form_layout = QFormLayout()
        form_widget.setLayout(self.form_layout)  # Sets the layout
        v_layout.addWidget(form_widget)  # Makes sure the text boxes are added.

        name_label = QLabel(self)  # Adds the name for the textbox
        name_label.setText("Name")
        self.name_textbox = QLineEdit(self)  # Makes the name textbox
        self.name_textbox.setText(body.name)
        self.form_layout.addRow(name_label, self.name_textbox)  # Adds the widgets to the form.

        self.colour = QColor(body.color)  # Fancy colours.

        colour_label = QLabel(self)  # Makes the colour label
        colour_label.setText("Colour")
        self.colour_button = QPushButton(self)  # Makes the colour button
        self.colour_button.setText("Edit")
        self.set_colour_button_colour()  # Dynamically changes the button colour to its selected color.
        self.colour_button.clicked.connect(self.change_colour)
        self.form_layout.addRow(colour_label, self.colour_button)

        self.mass_edit = self.make_number_edit("Mass", "mass")  # Names for all of the add / edit body button.
        self.pos_x_edit = self.make_number_edit("Position X", "pos_x")
        self.pos_y_edit = self.make_number_edit("Position Y", "pos_y")
        self.pos_z_edit = self.make_number_edit("Position Z", "pos_z")
        self.vel_x_edit = self.make_number_edit("Velocity X", "vel_x")
        self.vel_y_edit = self.make_number_edit("Velocity Y", "vel_y")
        self.vel_z_edit = self.make_number_edit("Velocity Z", "vel_z")

        ok_button = QPushButton(self)  # The ok button.
        ok_button.setText("Ok")
        ok_button.clicked.connect(self.confirm)
        v_layout.addWidget(ok_button)  # ok

    def set_colour_button_colour(self):  # Set the colour of the button.
        self.colour_button.setStyleSheet(f"background-color: {self.colour.name()}")

    def change_colour(self):  # When you click the colour button, opens a colour picker!
        dialog = QColorDialog(self.colour)
        if dialog.exec_() == QDialog.Accepted:
            self.colour = dialog.selectedColor()
            self.set_colour_button_colour()  # Sets the colour.

    # Makes a label for what we want to edit, and a textbox containing default value.
    def make_number_edit(self, text, attribute_name):
        default_value = getattr(self.body, attribute_name)

        label = QLabel(self)  # Makes the label
        label.setText(f"{text} ({default_value:.2e})")  # Sets the text
        label.setMinimumWidth(200)

        line_edit = QLineEdit(self)  # Makes the textbox
        line_edit.setMinimumWidth(400)  # To help with precision as it converts from float -> string -> float
        line_edit.setAlignment(Qt.AlignRight)

        # Sets the default text. getattr lets us get a variable name by specifying a string, and it will find it.
        # EG mass gotten from n ball
        line_edit.setText("%.9f" % default_value)

        self.form_layout.addRow(label, line_edit)  # Formats the text boxes onto the correct positions.

        def eval_line_edit():  # This will allow us to do some fancy maths with the mass and velocity EG 4e10, 4e9*10*20
            try:
                value = eval(line_edit.text(), {"sin": sin_deg, "cos": cos_deg})  # Get the text in dialog box
                if type(value) == int or type(value) == float:  # Check if what user entered is evaluated to number
                    line_edit.setText("%.9f" % float(value))  # Do fancy math.
                    label.setText(f"{text} ({value:.2e})")  # Adds scientific notation for easier read
                else:
                    line_edit.setText("%.9f" % default_value)  # Else reset back to default values
                    label.setText(f"{text} ({default_value:.2e})")

            except:
                # If there was an error evaluating, reset it to default
                line_edit.setText("%.9f" % default_value)
                label.setText(f"{text} ({default_value:.2e})")

        line_edit.editingFinished.connect(eval_line_edit)  # When finish editing textbox, try to evaluate as maths.

        return line_edit

    def confirm(self):  # This will update all the values on the ball
        self.body.name = self.name_textbox.text()
        self.body.mass = float(self.mass_edit.text())
        self.body.pos_x = float(self.pos_x_edit.text())
        self.body.pos_y = float(self.pos_y_edit.text())
        self.body.pos_z = float(self.pos_z_edit.text())
        self.body.vel_x = float(self.vel_x_edit.text())
        self.body.vel_y = float(self.vel_y_edit.text())
        self.body.vel_z = float(self.vel_z_edit.text())
        self.body.color = self.colour.name(QColor.HexRgb)

        self.close()
