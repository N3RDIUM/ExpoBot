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
# If the "speech_tts" folder doesn't exist, create it
if [ ! -d "speech_tts" ]; then
  mkdir speech_tts
fi
# If the "cache.json" file doesn't exist, create it
if [ ! -f "cache.json" ]; then
  echo "{\n\t\"train-data-hash\":\"\"}" > cache.json
fi
# If the "Feedback/feedbacks.csv" file doesn't exist, create it
if [ ! -f "Feedback/feedbacks.csv" ]; then
  echo "id,feedback\n" > Feedback/feedbacks.csv
fi

python3 UIBot/main.py