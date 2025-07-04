import cv2
import numpy as np
import find_marker  # Read README
import A_utility
import setting
import time
from filterpy.gh import GHFilter

##====== CAMERA CAPTURE W x H  = 800 x 600
cam = cv2.VideoCapture(0)  ## Webcam index here
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
print("W x H", cam.get(cv2.CAP_PROP_FRAME_WIDTH), cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

## Init marker tracking components
setting.init()
m = find_marker.Matching(  # Instance of the find_marker library
    N_=setting.N_,
    M_=setting.M_,
    fps_=setting.fps_,
    x0_=setting.x0_,
    y0_=setting.y0_,
    dx_=setting.dx_,
    dy_=setting.dy_,
)


count = 0
frame0 = None


## GH Filter, Change co-efficient
filter = GHFilter
G_coeff = 0.5  # High G, measurement influences more than prediction for the state x
H_coeff = 0.3  # High H, measurement influences more than prediction for the change in state dx


while True:
    count += 1
    start = time.time()
    frame = A_utility.get_processed_frame(cam)
    ## Contact Area
    if count == 1:
        frame0 = A_utility.get_processed_frame(cam)
        frame0_final = A_utility.inpaint(frame0)

    frame_final = A_utility.inpaint(frame)
    # frame_final = frame

    contact_area_dilated = A_utility.difference(frame_final, frame0_final, debug=False)
    contours = A_utility.get_all_contour(contact_area_dilated, frame, debug=False)

    hull_area, hull_mask, slope, center = A_utility.get_convex_hull_area(
        contact_area_dilated, frame, debug=True
    )  # Hull area and slope

    ## Marker
    m_centers = A_utility.marker_center(frame, debug=False)
    m.init(m_centers)
    m.run()
    flow = m.get_flow()  # FLOW
    """
    output: (Ox, Oy, Cx, Cy, Occupied) = flow
        Ox, Oy: N*M matrix, the x and y coordinate of each marker at frame 0
        Cx, Cy: N*M matrix, the x and y coordinate of each marker at current frame
        Occupied: N*M matrix, the index of the marker at each position, -1 means inferred. 
            e.g. Occupied[i][j] = k, meaning the marker mc[k] lies in row i, column j.
    """
    frame_flow = A_utility.draw_flow(frame, flow)

    frame_flow_hull, average_flow_change_in_hull = A_utility.draw_flow_mask(
        frame, flow, hull_mask, debug=True
    )

    """ Things you have
    flow
    hull_area


    contours
    contact_area_dilated

    """

    # Show frame
    if True:
        #     cv2.imshow("frame0", frame0)
        #     cv2.imshow("frame0_final", frame0_final)
        #     cv2.imshow("frame", frame)
        #     cv2.imshow("frame_final", frame_final)
        cv2.imshow("frame_flow", frame_flow)
        cv2.imshow("frame_flow_hull", frame_flow_hull)

    # End loop, print FPS
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    print("FPS", 1 / (time.time() - start))

cv2.destroyAllWindows()
