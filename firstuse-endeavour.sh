yay -S espeak freeglut glu
source ../bin/activate
git pull
pip install -r requirements.txt -v

echo "===================="
echo "WARNING: Please run localai-firstuse.sh first!"
echo "===================="

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
  echo "{\"OLD_HARDWARE\":0,\"PORT\":3030, \"CAMERA\":0,\"OPENAI_API_KEY\":""}" > config.json
  echo "===================="
  echo "WARNING: ExpoBot will not run unless you set the OpenAI Api Key in config.json!\nPlease do so."
  echo "Or you can use the localai backends!"
  echo "===================="
fi
# If the "tts_cache" folder doesn't exist, create it
if [ ! -d "tts_cache" ]; then
  mkdir tts_cache
fi

chmod +x ./start-localai.sh
./start-localai-firstuse.sh

python3 UIBot/main.py