import threading
from typing import NamedTuple, Optional, List, Union

from transcribe import Transcribe, TranscriptionOptions
from utils import make_safe, format_timestamp, _get_colored_text


class MainTask(NamedTuple):
    beam_size: int
    best_of: int
    patience: float
    length_penalty: float
    log_prob_threshold: Optional[float]
    no_speech_threshold: Optional[float]
    compression_ratio_threshold: Optional[float]
    condition_on_previous_text: bool
    temperature: List[float]
    initial_prompt: Optional[str]
    suppress_tokens: Optional[List[int]]
    word_timestamps: bool
    print_colors: bool
    verbose: bool

    _print = print
    mutex = threading.Lock()

    def print_text(self, segment):
        if self.print_colors and segment.words:
            text = _get_colored_text(segment.words)
        else:
            text = segment.text

        line = f"[{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}] {text}"
        with self.mutex:
            self._print(make_safe(line))

    def process(self, segment):
        # start, end, text = segment.start, segment.end, segment.text
        if self.verbose:
            print_thread = threading.Thread(target=self.print_text, args=(segment,))
            print_thread.start()

    def tasks(self,
              audio: str,
              model_path: str,
              output_dir: str,
              output_format: str,
              task: str,
              language: str,
              threads: int,
              device: str,
              device_index: Union[int, List[int]],
              compute_type: str):
        options = TranscriptionOptions(
            beam_size=self.beam_size,
            best_of=self.best_of,
            patience=self.patience,
            length_penalty=self.length_penalty,
            log_prob_threshold=self.log_prob_threshold,
            no_speech_threshold=self.no_speech_threshold,
            compression_ratio_threshold=self.compression_ratio_threshold,
            condition_on_previous_text=self.condition_on_previous_text,
            temperature=self.temperature,
            initial_prompt=self.initial_prompt,
            suppress_tokens=self.suppress_tokens,
            word_timestamps=self.word_timestamps,
            print_colors=self.print_colors)

        Transcribe().inference(
            audio,
            model_path,
            output_dir,
            output_format,
            task,
            language,
            threads,
            device,
            device_index,
            compute_type,
            self.verbose,
            options,
            self.process
        )
