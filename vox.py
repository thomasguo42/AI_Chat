import torch
import soundfile as sf
import os
from voxcpm import VoxCPM

def main():
    # 1. Initialize the model
    # It automatically detects if a GPU is available.
    print("Loading model...")
    model = VoxCPM.from_pretrained("openbmb/VoxCPM1.5")

    # 2. File Paths (Ensure these files exist in your current folder)
    input_mp3 = "gaoyuliang.MP3"
    wav_path = "reference_audio.wav"
    output_filename = "cloned_voice_output.wav"

    # 3. Convert MP3 to WAV using system command if wav doesn't exist
    if not os.path.exists(wav_path):
        print(f"Converting {input_mp3} to WAV...")
        os.system(f'ffmpeg -i "{input_mp3}" -ar 44100 "{wav_path}" -y')

    # 4. Input Configuration
    reference_transcript = (
        "有许多人凭着自身的努力或者说幸运站在了潮头之上，在潮头之上是风光无限、诱惑无限，也风险无限，"
        "就看你如何把握了。看未来远不如看过去要来得清楚，激昂和困惑交织在每一个人的心头，"
        "要留一份敬畏在心中，看别的可以模糊，但看底线一定要清楚。"
    )
    
    target_text = "Hello, this is a test of the voice cloning system running in a standalone terminal environment."

    # 5. Generate
    print("Generating audio... (using cuDNN if GPU is available)")
    try:
        output_audio = model.generate(
            text=target_text,
            prompt_wav_path=wav_path,
            prompt_text=reference_transcript
        )

        # 6. Save output
        sf.write(output_filename, output_audio, 44100)
        print(f"Success! Audio saved to: {os.path.abspath(output_filename)}")

    except Exception as e:
        print(f"An error occurred during generation: {e}")

if __name__ == "__main__":
    main()