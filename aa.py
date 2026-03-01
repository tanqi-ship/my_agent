# download_model.py
from huggingface_hub import snapshot_download
import os

# 使用国内镜像加速
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

snapshot_download(
    repo_id="shibing624/text2vec-base-chinese",
    local_dir=r"E:\MyPythonProject\my_agent\models\text2vec-base-chinese",
    local_dir_use_symlinks=False
)