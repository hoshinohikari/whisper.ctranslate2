# whisper.ctranslate2

****
|Author|HoshinoKun|
|---|---
|E-mail|hoshinokun@346pro.club
****

This is a whisper based on the [ctranslate2](https://opennmt.net/CTranslate2/) fine-tuned version that significantly reduces memory usage and optimizes speed. The code was partially referenced from [whisper-ctranslate2](https://github.com/jordimas/whisper-ctranslate2) and compiled as a native version using nuitka, and is now released on Releases.

## Usage
Download from [Releases](https://github.com/hoshinohikari/whisper.ctranslate2/releases)

```
fast-whisper2ass.exe audio --modle base
```

### Source Running
```
git clone https://github.com/hoshinohikari/whisper.ctranslate2.git
cd whisper.ctranslate2
pip install -r requirements.txt
python fast-whisper2ass.py audio --modle base
```

The Releases version includes the CUDA runtime library. If you need to run the source code version, please install CUDA 11 and cuDNN 8 on your own.

## Q&A
If you encounter any of these problems during use, you can try these solutions

1. FileNotFoundError  
Please download an ffmpeg.exe and place it in the same directory as fast-whisper2ass.exe.