import gradio as gr
from models import build_model
import torch
import numpy as np
import os
from kokoro import generate

SAMPLE_RATE = 24000
device = "cuda" if torch.cuda.is_available() else "cpu"

# Function to get available voices
def get_available_voices():
    voices_folder = "voices"
    voices = [f.split(".")[0] for f in os.listdir(voices_folder) if f.endswith(".pt")]
    return voices

# Function to get sample texts
def get_sample_texts():
    return [
        "Hello! This is a test of the Kokoro text-to-speech model.",
        "Welcome to the future of text-to-speech technology.",
        "Gradio makes building machine learning demos simple and effective.",
        "Try converting your own text into high-quality speech today!"
    ]

# Initialize model
MODEL = build_model("kokoro-v0_19.pth", device)

# Text-to-speech function
def text_to_speech(text, voice_name):
    """
    Convert input text to speech using the Kokoro model
    """
    audio = []
    # Load selected voice
    voicepack = torch.load(f"voices/{voice_name}.pt", weights_only=True).to(device)

    for chunk in text.split("."):
        if len(chunk) < 2:
            continue
        snippet, _ = generate(MODEL, chunk, voicepack, lang=voice_name[0])
        audio.extend(snippet)

    # Convert to numpy array for Gradio
    audio_array = np.array(audio)
    return (SAMPLE_RATE, audio_array)

# Create Gradio interface
with gr.Blocks(title="Kokoro Text-to-Speech") as demo:
    gr.Markdown(
        """# Kokoro Text-to-Speech Demo

Easily convert text to speech with the Kokoro model. Select a voice and input your desired text to generate high-quality audio output. Use the sample texts dropdown for inspiration if needed.
        """
    )

    with gr.Row():
        with gr.Column():
            sample_text_dropdown = gr.Dropdown(
                label="Sample Texts",
                choices=get_sample_texts(),
                value=None,
                interactive=True
            )

            text_input = gr.Textbox(
                label="Input Text",
                placeholder="Enter the text you want to convert to speech...",
                lines=5
            )

            sample_text_dropdown.change(
                fn=lambda text: text,
                inputs=sample_text_dropdown,
                outputs=text_input
            )

            voice_dropdown = gr.Dropdown(
                label="Select Voice",
                choices=get_available_voices(),
                value="af_bella"  # Default voice
            )

            generate_btn = gr.Button("Generate Speech", variant="primary")

        with gr.Column():
            audio_output = gr.Audio(
                label="Generated Speech",
                type="numpy"
            )

    # Link button to function
    generate_btn.click(
        fn=text_to_speech,
        inputs=[text_input, voice_dropdown],
        outputs=audio_output
    )

if __name__ == "__main__":
    demo.launch(share=True)
