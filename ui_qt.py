# ui_streamlit.py  –  minimal Streamlit UI with 1-row material bar + live video
import streamlit as st, subprocess, json, psutil, signal, time, cv2, os
from pathlib import Path

SCRIPT      = "live_demo_ur5.py"
FRAME_FILE  = "/tmp/gelsight_live.jpg"
PRED_FILE   = "/tmp/gelsight_pred.txt"
MATERIALS   = [f"Material {i}" for i in range(1,11)]     # labels to show

# ── sidebar – choose model + pose, start/abort ──────────────────────────────
st.sidebar.title("GelSight UR-5 Demo")

models = sorted(p.name for p in Path(".").glob("*.pt"))
model_choice = st.sidebar.selectbox("Model checkpoint", models)

poses = {
    "Pose A (6 mm)": ([0.635,0.123,0.024,-1.79,-0.68,-1.78], 6.0,0.02,0.02),
    "Pose B (5 mm)": ([0.625,0.118,0.031,-1.70,-0.80,-1.76], 5.0,0.02,0.02),
}
pose_choice = st.sidebar.selectbox("Pose preset", list(poses))

start_btn = st.sidebar.button("▶ Start")
stop_btn  = st.sidebar.button("⏹ Abort", type="primary")

if "proc" not in st.session_state: st.session_state["proc"] = None
proc = st.session_state["proc"]

# ── helpers to launch / stop subprocess ─────────────────────────────────────
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

# ── main layout – one row of labels + video frame ───────────────────────────
st.title("GelSight Live Prediction")

cols = st.columns(len(MATERIALS))           # 10 side-by-side slots
for col, name in zip(cols, MATERIALS):
    col.markdown(name, unsafe_allow_html=True)

frame_area = st.image([])

# ── refresh loop – updates every 60 ms ──────────────────────────────────────
while True:
    time.sleep(0.06)

    # update label highlight
    pred_id = None
    if os.path.exists(PRED_FILE):
        try:
            pred_id = int(open(PRED_FILE).read().strip())
        except ValueError:
            pass

    for i, (col, name) in enumerate(zip(cols, MATERIALS), 1):
        if i == pred_id:
            col.markdown(f"<span style='color:#17c207;font-weight:700'>{name}</span>",
                         unsafe_allow_html=True)
        else:
            col.markdown(name, unsafe_allow_html=True)

    # update frame
    if os.path.exists(FRAME_FILE):
        img = cv2.imread(FRAME_FILE)
        if img is not None:
            frame_area.image(img[:, :, ::-1], channels="RGB", use_column_width=True)

    # stop refreshing if subprocess is dead and user hasn’t restarted
    if st.session_state["proc"] is None:
        time.sleep(0.4)
