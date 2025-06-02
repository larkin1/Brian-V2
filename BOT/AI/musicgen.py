# Function to generate a song using ACE-Step

def getsong(prompt: str, duration: str, lyrics:str) -> str:
    """Generates a song using ACE-Step. Returns the path to the song file."""
    from gradio_client import Client # We import this here for a faster startup time as it is not commonly used.
    client = Client("ACE-Step/ACE-Step")
    result = client.predict(
            audio_duration=int(duration),
            prompt=prompt,
            lyrics=lyrics,
            infer_step=120,
            guidance_scale=15,
            scheduler_type="euler",
            cfg_type="apg",
            omega_scale=10,
            manual_seeds=None,
            guidance_interval=0.5,
            guidance_interval_decay=0,
            min_guidance_scale=3,
            use_erg_tag=True,
            use_erg_lyric=False,
            use_erg_diffusion=True,
            oss_steps=None,
            guidance_scale_text=0,
            guidance_scale_lyric=0,
            audio2audio_enable=False,
            ref_audio_strength=0.5,
            ref_audio_input=None,
            lora_name_or_path="none",
            api_name="/__call__"
    )
    print(result)
    return result[0]

def musicgen(data: dict, client) -> str:
    client.sendText(data['chatId'], "Generating song...")