#!/bin/bash
# from https://github.com/myshell-ai/MeloTTS/blob/main/docs/install.md
git clone https://github.com/myshell-ai/MeloTTS.git
cd MeloTTS
printf "\nbotocore>=1.34.98\ncached_path>=1.6.2" >> requirements.txt # from https://github.com/myshell-ai/MeloTTS/pull/124
pip install -e .
python -m unidic download