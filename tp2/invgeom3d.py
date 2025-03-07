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

# --- Add ball to represent target
# Add a vizualization for the target
ballID = "world/ball"
viz.addSphere(ballID, 0.05, "green")
# %jupyter_snippet 1
# Add a vizualisation for the tip of the arm.
tipID = "world/blue"
viz.addBox(tipID, [0.08] * 3, [0.2, 0.2, 1.0, 0.5])
#
# OPTIM 3D #########################################################
#


def cost(q):
    """Compute score from a configuration"""
    p = robot.placement(q, 6).translation
    return norm(p - target) ** 2


def callback(q):
    viz.applyConfiguration(ballID, target.tolist() + [0, 1, 0, 0])
    viz.applyConfiguration(tipID, robot.placement(q, 6))
    viz.display(q)
    time.sleep(1e-2)


target = np.array([0.5, 0.1, 0.2])  # x,y,z
qopt = fmin_bfgs(cost, robot.q0, callback=callback)
# %end_jupyter_snippet


##########################################################################
### This last part is to automatically validate the versions of this example.
class InvGeom3DTest(unittest.TestCase):
    def test_qopt_translation(self):
        self.assertTrue(
            (np.abs(target - robot.placement(qopt, 6).translation) < 1e-4).all()
        )


### TEST ZONE ############################################################
### Some asserts below to check the behavior of this script in stand-alone
class InvGeom3DTest2(unittest.TestCase):
    def test_qopt_3d(self):
        self.assertTrue(qopt.shape == (6,))
        self.assertTrue(
            np.allclose(qopt[:4], [-0.01835614, -0.94468605, 1.47944778, 0.67266344])
        )
        self.assertTrue(np.linalg.norm(qopt[4:]) == 0.0)


InvGeom3DTest2().test_qopt_3d()
