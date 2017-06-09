ffmpeg -i Gram_WK.mp4 -i Gram_Sem_resized.mp4 -filter_complex  "[0:v]setpts=PTS-STARTPTS, pad=iw:ih*2[bg]; [1:v]setpts=PTS-STARTPTS[fg]; [bg][fg]overlay=0:main_h/2" output.mp4
