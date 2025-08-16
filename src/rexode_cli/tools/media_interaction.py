import pyautogui
from playsound import playsound
import pyaudio
import wave
import cv2

def play_media(file_path):
    """Plays a media file."""
    try:
        playsound(file_path)
        return f"Successfully played {file_path}"
    except Exception as e:
        return f"Error playing media: {e}"

def capture_screenshot(save_path):
    """Captures a screenshot."""
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)
        return f"Successfully captured screenshot to {save_path}"
    except Exception as e:
        return f"Error capturing screenshot: {e}"

def record_audio(duration, save_path):
    """Records audio from the microphone."""
    try:
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 2
        fs = 44100
        p = pyaudio.PyAudio()
        stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)
        frames = []
        for i in range(0, int(fs / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(save_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()
        return f"Successfully recorded audio to {save_path}"
    except Exception as e:
        return f"Error recording audio: {e}"

def record_video(duration, save_path):
    """Records video from the camera."""
    try:
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(save_path, fourcc, 20.0, (640, 480))
        start_time = cv2.getTickCount()
        while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        return f"Successfully recorded video to {save_path}"
    except Exception as e:
        return f"Error recording video: {e}"

def image_search(query):
    """Searches for images on the web."""
    # This is a placeholder and would require integration with an image search API (e.g., Google Custom Search API)
    return f"Searched for images with query: {query}"

def generate_image(prompt):
    """Generates an image from a text prompt."""
    # This is a placeholder and would require integration with an image generation API (e.g., DALL-E, Midjourney)
    return f"Generated image with prompt: {prompt}"
