"""
Stand-alone inverse geom in 3D.  Given a reference translation <target> ,
it computes the configuration of the UR5 so that the end-effector position (3D)
matches the target. This is done using BFGS solver. While iterating to compute
the optimal configuration, the script also display the successive candidate
solution, hence moving the robot from the initial guess configuaration to the
reference target.
"""

import time
import unittest

import example_robot_data as robex
import numpy as np
import pinocchio as pin
from numpy.linalg import norm
from scipy.optimize import fmin_bfgs

from supaero2023.meshcat_viewer_wrapper import MeshcatVisualizer

# --- Load robot model
robot = robex.load("ur5")
NQ = robot.model.nq
NV = robot.model.nv

# Open the viewer
viz = MeshcatVisualizer(robot)

# Define an init config
robot.q0 = np.array([0, -3.14 / 2, 0, 0, 0, 0])
viz.display(robot.q0)
time.sleep(0.3)
print("Let's go to pdes.")

# --- Add box to represent target
# Add a vizualization for the target
boxID = "world/box"
viz.addBox(boxID, [0.05, 0.1, 0.2], [1.0, 0.2, 0.2, 0.5])
# %jupyter_snippet 1
# Add a vizualisation for the tip of the arm.
tipID = "world/blue"
viz.addBox(tipID, [0.08] * 3, [0.2, 0.2, 1.0, 0.5])

#
# OPTIM 6D #########################################################
#


def cost(q):
    """Compute score from a configuration"""
    M = robot.placement(q, 6)
    return norm(pin.log(M.inverse() * Mtarget).vector)


def callback(q):
    viz.applyConfiguration(boxID, Mtarget)
    viz.applyConfiguration(tipID, robot.placement(q, 6))
    viz.display(q)
    time.sleep(1e-1)


Mtarget = pin.SE3(pin.utils.rotate("x", 3.14 / 4), np.array([-0.5, 0.1, 0.2]))  # x,y,z
qopt = fmin_bfgs(cost, robot.q0, callback=callback)

print("The robot finally reached effector placement at\n", robot.placement(qopt, 6))
# %end_jupyter_snippet


### TEST ZONE ############################################################
### Some asserts below to check the behavior of this script in stand-alone
class InvGeom6DTest(unittest.TestCase):
    def test_qopt_6d(self):
        Mopt = robot.placement(qopt, 6)
        self.assertTrue((np.abs(Mtarget.translation - Mopt.translation) < 1e-7).all())
        self.assertTrue(np.allclose(pin.log(Mtarget.inverse() * Mopt).vector, 0))


InvGeom6DTest().test_qopt_6d()
