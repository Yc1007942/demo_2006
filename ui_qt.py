"""streamlit run ui_qt.py
"""
import streamlit as st, subprocess, json, psutil, signal, time, cv2, os
from pathlib import Path

SCRIPT      = "live_demo_ur5.py"
FRAME_FILE  = "/tmp/gelsight_live.jpg"
PRED_FILE   = "/tmp/gelsight_pred.txt"
MATERIALS   = [f"Material {i}" for i in range(1,11)]    
st.sidebar.title("GelSight UR-5 Demo")
models = sorted(p.name for p in Path(".").glob("*.pt"))
model_choice = st.sidebar.selectbox("Model checkpoint", models)
poses = {
    "Index position": ([  0.481,  0.136, -0.111,  2.889,  1.232,  0.001 ], 6.0,0.02,0.02),
    "Position A": ([  0.432,  0.206, -0.111, -2.886, -1.231, -0.029 ], 6.0, 0.001, 0.01),
    "Position B":([  0.511,  0.139, -0.110, -2.886, -1.231, -0.029 ], 6.0, 0.001, 0.01),
    "Position C":([  0.587,  0.073, -0.111, -2.886, -1.231, -0.029 ], 6.0, 0.001, 0.01),
    "Position D":([  0.646,  0.147, -0.109, -2.886, -1.231, -0.029 ], 6.0, 0.001, 0.01),
    "Position E":([  0.576,  0.215, -0.112, -2.885, -1.230, -0.042 ], 6.0, 0.001, 0.01),
    "Position F":([  0.496,  0.277, -0.111, -2.886, -1.231, -0.029 ], 6.0, 0.001, 0.01),
    "Position G":([  0.559,  0.361, -0.111, -2.884, -1.230, -0.037 ], 6.0, 0.001, 0.01),
    "Position H":([  0.637,  0.293, -0.110, -2.886, -1.231, -0.033 ], 6.0, 0.001, 0.01),
    "Position I":([  0.712,  0.227, -0.110, -2.886, -1.230, -0.039 ], 6.0, 0.001, 0.01),
}
pose_choice = st.sidebar.selectbox("Pose preset", list(poses))
start_btn = st.sidebar.button("▶ Start")
stop_btn  = st.sidebar.button("⏹ Abort", type="primary")
if "proc" not in st.session_state: st.session_state["proc"] = None
proc = st.session_state["proc"]
def launch():
    cfg = json.dumps({"MODEL_FILES":[model_choice],"POSES":[poses[pose_choice]]})
    st.session_state["proc"] = subprocess.Popen(
        ["python", SCRIPT, cfg],
        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
def abort():
    p = st.session_state["proc"]
    if p and psutil.pid_exists(p.pid):
        psutil.Process(p.pid).send_signal(signal.SIGINT)
    st.session_state["proc"] = None
if start_btn and not proc: launch()
if stop_btn  and proc:     abort()
st.title("GelSight Live Prediction")

cols          = st.columns(len(MATERIALS))        
placeholders  = [col.empty() for col in cols]    
for ph, name in zip(placeholders, MATERIALS):      
    ph.markdown(name, unsafe_allow_html=True)

frame_area = st.image([])
while True:
    time.sleep(0.06)
    pred_id = None
    if os.path.exists(PRED_FILE):
        try:    pred_id = int(open(PRED_FILE).read().strip())
        except: pred_id = None
    for i, (ph, name) in enumerate(zip(placeholders, MATERIALS), 1):
        if i == pred_id:
            ph.markdown(f"<span style='color:#17c207;font-weight:700'>{name}</span>",
                        unsafe_allow_html=True)
        else:
            ph.markdown(name, unsafe_allow_html=True)

    if os.path.exists(FRAME_FILE):
        img = cv2.imread(FRAME_FILE)
        if img is not None:
            frame_area.image(img[:, :, ::-1], channels="RGB",
                             use_container_width=True)

    if st.session_state["proc"] is None:
        time.sleep(0.4)