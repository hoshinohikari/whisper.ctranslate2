from typing import NamedTuple, Optional, List, Union

import tqdm

from faster_whisper import WhisperModel


class TranscriptionOptions(NamedTuple):
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


class Transcribe:
    def inference(
            self,
            audio: str,
            model_path: str,
            output_dir: str,
            output_format: str,
            task: str,
            language: str,
            threads: int,
            device: str,
            device_index: Union[int, List[int]],
            compute_type: str,
            verbose: bool,
            options: TranscriptionOptions,
            callback
    ):
        model = WhisperModel(
            model_path,
            device=device,
            device_index=device_index,
            compute_type=compute_type,
            cpu_threads=threads,
        )

        segments, info = model.transcribe(
            audio=audio,
            language=language,
            task=task,
            beam_size=options.beam_size,
            best_of=options.best_of,
            patience=options.patience,
            length_penalty=options.length_penalty,
            temperature=options.temperature,
            compression_ratio_threshold=options.compression_ratio_threshold,
            log_prob_threshold=options.log_prob_threshold,
            no_speech_threshold=options.no_speech_threshold,
            condition_on_previous_text=options.condition_on_previous_text,
            initial_prompt=options.initial_prompt,
            word_timestamps=True if options.print_colors else options.word_timestamps,
        )

        print(
            "Detected language '%s' with probability %f"
            % (info.language, info.language_probability)
        )

        with tqdm.tqdm(
                total=info.duration, unit="seconds", disable=verbose is not False
        ) as pbar:
            for segment in segments:
                callback(segment)
