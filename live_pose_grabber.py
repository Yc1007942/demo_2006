#!/usr/bin/env python3
"""
python live_pose_grabber.py  
"""

import argparse, sys, time
import numpy as np
from rtde_receive import RTDEReceiveInterface

ROBOT_IP, PORT = "10.10.10.1", 50002

def fmt_pose(p):
    return "[ " + ", ".join(f"{v: .3f}" for v in p) + " ]"

def main(a):
    recv = RTDEReceiveInterface(ROBOT_IP)
    print("Connected.  Move the robot, press <Enter> to capture, 'q'+<Enter> to quit.")

    baseline = None
    if a.origin_joints:
        baseline = np.radians([float(x) for x in a.origin_joints])

    while True:
        key = input("> ")
        if key.strip().lower() == "q":
            break

        pose = recv.getActualTCPPose()          # 6 floats (m & rad)
        joints = np.array(recv.getActualQ())    # 6 floats (rad)

        if baseline is None:
            baseline = joints
            print("Baseline set.")

        dJ_deg = np.degrees(joints - baseline)
        tuple_line = (f"({fmt_pose(pose)}, "
                      f"{a.depth_mm}, {a.speed}, {a.step_mm}, "
                      "[ " + ", ".join(f"{d:.1f}" for d in dJ_deg) + " ]),")
        print(tuple_line)

if __name__ == "__main__":
    P = argparse.ArgumentParser()
    P.add_argument("--depth-mm", type=float, default=0,
                   help="placeholder depth_mm value")
    P.add_argument("--speed",    type=float, default=0,
                   help="placeholder speed (m/s)")
    P.add_argument("--step-mm",  type=float, default=0,
                   help="placeholder step_mm")
    P.add_argument("--origin-joints", nargs=6, metavar=("J1","J2","J3","J4","J5","J6"),
                   help="baseline joint angles (deg); otherwise first sample is baseline")
    main(P.parse_args())
