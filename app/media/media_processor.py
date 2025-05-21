from app.config import FFMPEG_PATH, TEMP_BASE_DIR, VOSK_MODEL_DIR, AI_INPUT_IMAGES

import subprocess
import wave
import json
import os
import cv2

from vosk import Model, KaldiRecognizer


def get_video_duration(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("File cannot be opened.")
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = total_frames / fps
    cap.release()
    return duration


class MediaProcessor:
    def __init__(self, media):
        self.media_dir = os.path.join(TEMP_BASE_DIR, media)

        extension = media.rsplit(".", 1)[-1]
        self.media_name = media[:-(len(extension) + 1)] if f".{extension}" in media else media
        self.media_sound_dir = os.path.join(TEMP_BASE_DIR, f"{self.media_name}.wav")
        self.n_frames = int(AI_INPUT_IMAGES)

    def speech_to_text(self):
        self.extract_audio()
        text = self.audio_to_text()

        return text

    def get_media_name(self):
        return self.media_name

    def extract_frames(self):
        duration = get_video_duration(self.media_dir)
        timestamps = [(duration * i / (self.n_frames + 1)) for i in range(1, self.n_frames + 1)]

        output_paths = []

        for idx, timestamp in enumerate(timestamps):
            output_path = os.path.join(TEMP_BASE_DIR, f'{self.media_name}_frame_{idx:03}.png')
            command = [
                FFMPEG_PATH,
                '-loglevel', 'error',
                '-ss', f'{timestamp:.3f}',
                '-i', self.media_dir,
                '-vframes', '1',
                '-q:v', '2',
                output_path
            ]
            subprocess.run(command, check=True)
            output_paths.append(output_path)

        return output_paths

    def extract_audio(self):
        command = [FFMPEG_PATH, '-loglevel', 'error', '-i', self.media_dir, '-vn', '-acodec', 'pcm_s16le', '-ar',
                   '16000', '-ac', '1',
                   self.media_sound_dir]
        subprocess.run(command, check=True)

    def audio_to_text(self):
        wf = wave.open(self.media_sound_dir, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            raise ValueError("Audio must be WAV mono 16kHz PCM.")

        model = Model(VOSK_MODEL_DIR)
        rec = KaldiRecognizer(model, wf.getframerate())

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)

        final_res = json.loads(rec.FinalResult())
        return final_res.get("text", "")
