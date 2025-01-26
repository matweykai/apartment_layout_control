docker pull vllm/vllm-openai:latest

docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model mistralai/Pixtral-12B-2409

echo "Checking availability"
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"input": "Your input text here"}' && echo "Model is ready"
