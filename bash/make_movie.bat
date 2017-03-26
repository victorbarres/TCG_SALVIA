REM ffmpeg -f image2 -r 60 -i Grammatical_WM_P_concise%05d.gv.png -qscale:v 0 GramWM_state.avi
REM ffmpeg -f image2 -r 60 -i Grammatical_WM_P_concise%05d.gv.png -c:v mjpeg -qscale:v 0 GramWM_state.avi


start C:\ffmpeg\bin\ffmpeg.exe -f image2 -r 60 -i Grammatical_WM_P_concise%05d.gv.png -qscale:v 0 GramWM_state.avi