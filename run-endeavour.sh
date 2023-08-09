yay -S espeak freeglut glu
source ../bin/activate
git pull

# If the "faces" folder doesn't exist, create it
if [ ! -d "faces" ]; then
  mkdir faces
fi
# If the "feedback_recordings" folder doesn't exist, create it
if [ ! -d "feedback_recordings" ]; then
  mkdir feedback_recordings
fi
# If the "feedbacks.csv" file doesn't exist, create it
if [ ! -f "feedbacks.json" ]; then
  echo "{}" > feedbacks.json
fi
# If the "config.json" file doesn't exist, create it
if [ ! -f "config.json" ]; then
  echo "{\"OLD_HARDWARE\":0,\"PORT\":8080, \"CAMERA\":0}" > feedbacks.json
fi
# If the "tts_cache" folder doesn't exist, create it
if [ ! -d "tts_cache" ]; then
  mkdir tts_cache
fi

python3 UIBot/main.py