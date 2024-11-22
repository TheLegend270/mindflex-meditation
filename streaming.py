import queue
import threading
from functools import reduce
from typing import Callable, Generator
import openai
from flask import Response

# Constants
DELIMITERS = [f"{d} " for d in (".", "?", "!")]  # Determine where one phrase ends
MINIMUM_PHRASE_LENGTH = 200  # Minimum length of phrases to minimize audio choppiness
TTS_CHUNK_SIZE = 4096  # Increased chunk size for better audio quality

# Default values
DEFAULT_RESPONSE_MODEL = "gpt-3.5-turbo"
DEFAULT_TTS_MODEL = "tts-1"
DEFAULT_VOICE = "onyx"

class StreamingManager:
    def __init__(self, client: openai.OpenAI):
        self.client = client
        self.stop_event = threading.Event()
        self.phrase_queue = queue.Queue()
        self.audio_queue = queue.Queue(maxsize=32)  # Buffer size for smoother playback

    def stream_delimited_completion(
        self,
        messages: list[dict],
        model: str = DEFAULT_RESPONSE_MODEL,
        content_transformers: list[Callable[[str], str]] = [],
        phrase_transformers: list[Callable[[str], str]] = [],
        delimiters: list[str] = DELIMITERS,
    ) -> Generator[str, None, None]:
        """Generates delimited phrases from OpenAI's chat completions."""
        def apply_transformers(s: str, transformers: list[Callable[[str], str]]) -> str:
            return reduce(lambda c, transformer: transformer(c), transformers, s)

        working_string = ""
        for chunk in self.client.chat.completions.create(
            messages=messages, model=model, stream=True
        ):
            if self.stop_event.is_set():
                yield None
                return

            content = chunk.choices[0].delta.content or ""
            if content:
                working_string += apply_transformers(content, content_transformers)
                while len(working_string) >= MINIMUM_PHRASE_LENGTH:
                    delimiter_index = -1
                    for delimiter in delimiters:
                        index = working_string.find(delimiter, MINIMUM_PHRASE_LENGTH)
                        if index != -1 and (delimiter_index == -1 or index < delimiter_index):
                            delimiter_index = index

                    if delimiter_index == -1:
                        break

                    phrase, working_string = (
                        working_string[: delimiter_index + len(delimiter)],
                        working_string[delimiter_index + len(delimiter) :],
                    )
                    yield apply_transformers(phrase, phrase_transformers)

        if working_string.strip():
            yield working_string.strip()

        yield None  # Sentinel value

    def phrase_generator(self, system_prompt: str, user_input: str):
        """Generates phrases and puts them in the phrase queue."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        for phrase in self.stream_delimited_completion(
            messages=messages,
            content_transformers=[lambda c: c.replace("\n", " ")],
            phrase_transformers=[lambda p: p.strip()],
        ):
            if phrase is None:
                self.phrase_queue.put(None)
                return
            self.phrase_queue.put(phrase)

    def text_to_speech_processor(self):
        """Processes phrases into speech and puts the audio in the audio queue."""
        while not self.stop_event.is_set():
            phrase = self.phrase_queue.get()
            if phrase is None:
                self.audio_queue.put(None)
                return

            try:
                with self.client.audio.speech.with_streaming_response.create(
                    model=DEFAULT_TTS_MODEL,
                    voice=DEFAULT_VOICE,
                    speed=0.75,  # Slower speed for more relaxing pace
                    response_format="mp3",
                    input=phrase
                ) as response:
                    # Collect a few chunks before starting playback
                    buffer = []
                    for i, chunk in enumerate(response.iter_bytes(chunk_size=TTS_CHUNK_SIZE)):
                        if i < 4:  # Buffer first 4 chunks
                            buffer.append(chunk)
                        else:
                            if buffer:
                                for buffered_chunk in buffer:
                                    self.audio_queue.put(buffered_chunk)
                                buffer = []
                            self.audio_queue.put(chunk)
                        if self.stop_event.is_set():
                            return
            except Exception as e:
                print(f"Error in text_to_speech_processor: {e}")
                self.audio_queue.put(None)
                return

    def stream_meditation(self, system_prompt: str, user_input: str):
        """Stream meditation text and audio."""
        def generate():
            # Start threads
            phrase_generation_thread = threading.Thread(
                target=self.phrase_generator,
                args=(system_prompt, user_input)
            )
            tts_thread = threading.Thread(
                target=self.text_to_speech_processor
            )

            phrase_generation_thread.start()
            tts_thread.start()

            # Stream audio chunks
            while True:
                chunk = self.audio_queue.get()
                if chunk is None:
                    break
                yield chunk

            # Clean up
            phrase_generation_thread.join()
            tts_thread.join()
            self.stop_event.clear()

        return Response(generate(), mimetype='audio/mpeg')
