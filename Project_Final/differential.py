# Newtons law of Gravity
import numpy as np


# Creates a ball class for better organisation.
class Ball:
    def __init__(self, name, mass=0.0, pos_x=0.0, vel_x=0.0, pos_y=0.0, vel_y=0.0, pos_z=0.0, vel_z=0.0, color="#FF00FF"):
        self.name = name
        self.mass = mass  # In kilograms for object n
        self.color = color

        # POSITIONS AND VELOCITIES (in meters)
        self.pos_x = pos_x
        self.vel_x = vel_x
        self.pos_y = pos_y
        self.vel_y = vel_y
        self.pos_z = pos_z
        self.vel_z = vel_z

        # AXIS FOR POS AND VEL
        self.pos_vector = None
        self.vel_vector = None

    # Sets the pos vector and the vel vector for a specific dimension.
    def clear_results(self, n_dimension):
        if n_dimension == 2:
            self.pos_vector = np.array([self.pos_x, self.pos_y], dtype=np.longdouble)  # Initial x, y position of ball, as well as general position
            self.vel_vector = np.array([self.vel_x, self.vel_y], dtype=np.longdouble)  # see above but for velocity.
        elif n_dimension == 3:
            self.pos_vector = np.array([self.pos_x, self.pos_y, self.pos_z], dtype=np.longdouble)
            self.vel_vector = np.array([self.vel_x, self.vel_y, self.vel_z], dtype=np.longdouble)
        else:
            raise ValueError("Bad number of dimensions")

    def serialize(self):  # To save the balls. PLEASE make sure the simulation works first before saving pls.
        return {
            "name": self.name,
            "mass": self.mass,
            "color": self.color,
            "pos_x": self.pos_x,
            "pos_y": self.pos_y,
            "pos_z": self.pos_z,
            "vel_x": self.vel_x,
            "vel_y": self.vel_y,
            "vel_z": self.vel_z,
        }

    def deserialize(self, info):  # To load the balls.
        self.name = info["name"]
        self.mass = info["mass"]
        self.color = info["color"]
        self.pos_x = info["pos_x"]
        self.pos_y = info["pos_y"]
        self.pos_z = info["pos_z"]
        self.vel_x = info["vel_x"]
        self.vel_y = info["vel_y"]
        self.vel_z = info["vel_z"]


########################################################################################################################################
# THIS CODE WAS USED TO CALCULATE THE ENERGY, BUT IT IS NOW OBSOLETE. Kept for historical reasons.
########################################################################################################################################
# def r_distance(pos_array_1, pos_array_2):
#     """
#     Calculates r distance, not x and y distance for the energy
#     """
#
#     dist_array = np.sqrt((pos_array_1[:, 0] - pos_array_2[:, 0]) ** 2 + (pos_array_1[:, 1] - pos_array_2[:, 1]) ** 2)
#
#     return dist_array
#
#
# # Calculating Energy.
# def calc_energy_2body(ball_n_1, ball_n_2, distance, vel_array_1, vel_array_2, G = 6.67408e-11):
#
#     # Extend this for 3D case as well, and multiple ball_n's.
#     vel_array_1 = np.sqrt(vel_array_1[:, 0] ** 2 + vel_array_1[:, 1] **2 )
#     vel_array_2 = np.sqrt(vel_array_2[:, 0] ** 2 + vel_array_2[:, 1] ** 2)
#
#     # Adding gravitational potential and kinetic energies.
#     energy = +(G*ball_n_1.mass*ball_n_2.mass / distance) - (0.5)*ball_n_1.mass*(vel_array_1**2) - (0.5)*ball_n_2.mass*(vel_array_2**2)
#
#     return energy
########################################################################################################################################


# Similar to above once again, but for n systems!
def distance_n(s1, s2, n_dimensions):
    """
    Calculate the total distance for a 2D object

    :param s1: Affected object
    :param s2: Transmitted object
    :param n_dimensions: Number of dimensions
    :return: The total distance
    Note: x = 0, y = 1, z = 2 for the dimensions.
    """

    if n_dimensions == 2:
        dist_tot = ((s2[0] - s1[0]) ** 2 + (s2[1] - s1[1]) ** 2) ** 0.5  # Because better than np.sqrt
    elif n_dimensions == 3:
        dist_tot = ((s2[0] - s1[0]) ** 2 + (s2[1] - s1[1]) ** 2 + (s2[2] - s1[2]) ** 2) ** 0.5
    else:
        raise ValueError("Bad n_dimensions")

    return dist_tot


# This figures distance. Similarly to above, s1 is affected object, s2 is transmitted object.
def distance_direction_n(s1, s2):
    dist_direction = s2 - s1
    return dist_direction


# The equation that the ODE solver will use.
def newton_newODE_solver_2(
        time,
        vectors,
        G,
        size_of_parameters,
        n_bodies,
        number_dimensions,
        ball_n,
        prog_dialog,
        max_time
):
    prog_dialog.setValue(time / max_time * 100)  # Sets progress bar time value.

    if number_dimensions != 2 and number_dimensions != 3:  # No, time does not count as the 4th dimension.
        return ValueError()

    vectors = np.reshape(vectors, size_of_parameters)  # Allows for easier logistical management of balls.

    # Creating a loop to generate the position vectors.

    n_count = 0

    # Sets up the initial arrays for the vectors.
    pos_vector_bodies = np.zeros([n_bodies, number_dimensions])
    vel_vector_bodies = np.zeros([n_bodies, number_dimensions])

    while n_count < n_bodies:  # Counts up until the max n_bodies.
        pos_vector_bodies[n_count, :] = vectors[n_count, :]
        vel_vector_bodies[n_count, :] = vectors[n_count + n_bodies, :]

        n_count += 1

    # Now we need to do the sums, and get the right answers.

    # Once again sets up the initial arrays.
    dposdt_n = np.zeros([n_bodies, number_dimensions])
    dveldt_n = np.zeros([n_bodies, number_dimensions])

    n_count = 0
    while n_count < n_bodies:  # Does for all bodies.

        # For Vectors
        dposdt_n[n_count, :] = vel_vector_bodies[n_count, :]

        object_affected_i = n_count  # Selects the objects to be affected by the gravi forces. Done for readability.
        object_transmitting_j = 0  # Selects the objects to transmit the gravi forces to.

        while object_transmitting_j < n_bodies:  # Now uses the transmitted object onto the object affected.

            # To ensure it ignores itself as it were.
            if object_transmitting_j != object_affected_i:

                # Pre-calculates the distance direction.
                distance_direction_body = distance_direction_n(
                    pos_vector_bodies[object_affected_i, :],
                    pos_vector_bodies[object_transmitting_j, :]
                )
                # Pre-calculates the total distance.
                distance_tot = distance_n(
                    pos_vector_bodies[object_affected_i, :],
                    pos_vector_bodies[object_transmitting_j, :],
                    number_dimensions
                )
                # Inputs into newtons 2nd law of gravity.
                dveldt_n[object_affected_i, :] = \
                    dveldt_n[object_affected_i, :] + \
                    ((G * ball_n[object_transmitting_j].mass * distance_direction_body) /
                     distance_tot ** 3)

            # Onto the next transmitted object.
            object_transmitting_j += 1

        # Onto the next body.
        n_count += 1

    # Prepares the gathered results for concatenation.
    vel_derivatives_n = dveldt_n.flatten()
    pos_derivatives_n = dposdt_n.flatten()

    # Otherwise odeint will scream at me.
    final_derivatives_n = np.concatenate((pos_derivatives_n, vel_derivatives_n))

    return final_derivatives_n
