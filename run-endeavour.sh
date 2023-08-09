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
if [ ! -f "feedbacks.csv" ]; then
  echo "id,feedback\n" > Feedback/feedbacks.csv
fi
# If the "tts_cache" folder doesn't exist, create it
if [ ! -d "tts_cache" ]; then
  mkdir tts_cache
fi

python3 UIBot/main.py