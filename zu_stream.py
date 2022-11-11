import os
import glob
import datetime as dt

import keyring
import streamlit as st

SEARCH_HOURS_SPAN = 11
SEARCH_MIN = 30
SEARCH_MIN_STEP = 30

if 'dt_load' not in st.session_state:
    st.session_state['dt_load'] = dt.datetime.now()

st.markdown('# Zu Live Streaming')
st.write(f'<img src="{keyring.get_password("zu", "zu1")}" style="width:100%">', unsafe_allow_html=True)

st.markdown('# Past Videos')

t_search = st.slider('Search back from:', min_value=(st.session_state.dt_load-dt.timedelta(hours=SEARCH_HOURS_SPAN)),
                     max_value=st.session_state.dt_load, step=dt.timedelta(minutes=SEARCH_MIN_STEP),
                     value=st.session_state.dt_load, format='HH:mm:ss')

videofiles = sorted(glob.glob('videos/*.mp4'), reverse=True)
for f in videofiles[1:]:
    fn = os.path.basename(f).replace('zu_record_', '').replace('.mp4', '')
    _dt = dt.datetime.strptime(fn, '%Y%m%d_%H%M%S')
    if ( (t_search - _dt).seconds <= 60*SEARCH_MIN and
         (t_search - _dt).seconds >= 0):
        st.markdown(f'## {_dt.strftime("%Y/%m/%d %H:%M:%S")}~ (5 mins)')
        with open(f, 'rb') as video:
            st.video(video)
