ffmpeg -i Phonological_WM_C_WM_inst_activity.mp4 -i WK_frame_WM_WM_inst_activity.mp4 -filter_complex  "[0:v]setpts=PTS-STARTPTS, pad=iw*2:ih[bg]; [1:v]setpts=PTS-STARTPTS[fg]; [bg][fg]overlay=w" output.mp4