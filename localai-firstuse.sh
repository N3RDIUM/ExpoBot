# Clone LocalAI
git clone https://github.com/go-skynet/LocalAI

cd LocalAI

# (optional) Checkout a specific LocalAI tag
# git checkout -b build <TAG>

# Download gpt4all-j to models/
wget https://gpt4all.io/models/ggml-gpt4all-j.bin -O models/ggml-gpt4all-j

# Use a template from the examples
cp -rf prompt-templates/ggml-gpt4all-j.tmpl models/

# (optional) Edit the .env file to set things like context size and threads
# vim .env

# start with docker-compose
echo "starting..."
docker-compose up -d --pull always
echo "testing..."
curl http://localhost:8080/v1/models
curl http://localhost:8080/v1/chat/completions -H "Content-Type: application/json" -d '{
     "model": "ggml-gpt4all-j",
     "messages": [{"role": "user", "content": "How are you?"}],
     "temperature": 0.9 
   }'