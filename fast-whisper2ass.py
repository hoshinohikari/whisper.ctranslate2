import argparse
import os
import warnings
from typing import Union, List

import numpy as np

from MainTask import MainTask
from faster_whisper import _MODELS
from languages import LANGUAGES, TO_LANGUAGE_CODE


def str2bool(string):
    str2val = {"True": True, "False": False}
    if string in str2val:
        return str2val[string]
    else:
        raise ValueError(f"Expected one of {set(str2val.keys())}, got {string}")


def optional_int(string):
    return None if string == "None" else int(string)


def optional_float(string):
    return None if string == "None" else float(string)


def _from_language_to_iso_code(language):
    if language is not None:
        language_name = language.lower()
        if language_name not in LANGUAGES:
            if language_name in TO_LANGUAGE_CODE:
                language = TO_LANGUAGE_CODE[language_name]

    return language


def read_command_line():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "audio", nargs="+", type=str, help="audio file(s) to transcribe"
    )
    parser.add_argument(
        "--model",
        default="small",
        choices=list(_MODELS),
        help="name of the Whisper model to use",
    )
    parser.add_argument(
        "--model_dir",
        type=str,
        default=None,
        help="the path to save model files; uses ~/.cache/whisper-ctranslate2 by default",
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        type=str,
        default=".",
        help="directory to save the outputs",
    )
    parser.add_argument(
        "--output_format",
        "-f",
        type=str,
        default="all",
        choices=["txt", "vtt", "srt", "tsv", "all"],
        help="format of the output file; if not specified, all available formats will be produced",
    )
    parser.add_argument(
        "--verbose",
        type=str2bool,
        default=True,
        help="whether to print out the progress and debug messages",
    )
    parser.add_argument(
        "--task",
        type=str,
        default="transcribe",
        choices=["transcribe", "translate"],
        help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')",
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        choices=sorted(LANGUAGES.keys()) + sorted([k.title() for k in TO_LANGUAGE_CODE.keys()]),
        help="language spoken in the audio, specify None to perform language detection",
    )
    parser.add_argument(
        "--threads",
        type=optional_int,
        default=0,
        help="number of threads used for CPU inference",
    )
    parser.add_argument(
        "--temperature", type=float, default=0, help="temperature to use for sampling"
    )
    parser.add_argument(
        "--temperature_increment_on_fallback",
        type=optional_float,
        default=0.2,
        help="temperature to increase when falling back when the decoding fails to meet either of the thresholds below",
    )
    parser.add_argument(
        "--best_of",
        type=optional_int,
        default=5,
        help="number of candidates when sampling with non-zero temperature",
    )
    parser.add_argument(
        "--beam_size",
        type=optional_int,
        default=5,
        help="number of beams in beam search, only applicable when temperature is zero",
    )
    parser.add_argument(
        "--patience",
        type=float,
        default=1.0,
        help="optional patience value to use in beam decoding, as in https://arxiv.org/abs/2204.05424, the default ("
             "1.0) is equivalent to conventional beam search",
    )
    parser.add_argument(
        "--length_penalty",
        type=float,
        default=1.0,
        help="optional token length penalty coefficient (alpha) as in https://arxiv.org/abs/1609.08144, uses simple "
             "length normalization by default",
    )
    parser.add_argument(
        "--suppress_tokens",
        type=str,
        default="-1",
        help="comma-separated list of token ids to suppress during sampling; '-1' will suppress most special "
             "characters except common punctuations",
    )
    parser.add_argument(
        "--initial_prompt",
        type=str,
        default=None,
        help="optional text to provide as a prompt for the first window.",
    )
    parser.add_argument(
        "--condition_on_previous_text",
        type=str2bool,
        default=True,
        help="if True, provide the previous output of the model as a prompt for the next window; disabling may make "
             "the text inconsistent across windows, but the model becomes less prone to getting stuck in a failure "
             "loop",
    )
    parser.add_argument(
        "--compression_ratio_threshold",
        type=optional_float,
        default=2.4,
        help="if the gzip compression ratio is higher than this value, treat the decoding as failed",
    )
    parser.add_argument(
        "--logprob_threshold",
        type=optional_float,
        default=-1.0,
        help="if the average log probability is lower than this value, treat the decoding as failed",
    )
    parser.add_argument(
        "--no_speech_threshold",
        type=optional_float,
        default=0.6,
        help="if the probability of the <|nospeech|> token is higher than this value AND the decoding has failed due "
             "to `logprob_threshold`, consider the segment as silence",
    )
    parser.add_argument(
        "--word_timestamps",
        type=str2bool,
        default=False,
        help="(experimental) extract word-level timestamps and refine the results based on them",
    )
    parser.add_argument(
        "--device", default="auto", help="device to use for CTranslate2 inference"
    )

    # CTranslate2 specific parameters
    parser.add_argument(
        "--device_index",
        nargs="*",
        type=int,
        default=0,
        help="Device IDs where to place this model on",
    )
    parser.add_argument(
        "--compute_type",
        choices=[
            "default",
            "auto",
            "int8",
            "int8_float16",
            "int16",
            "float16",
            "float32",
        ],
        default="auto",
        help="Type of quantization to use (see https://opennmt.net/CTranslate2/quantization.html)",
    )
    parser.add_argument(
        "--model_directory",
        type=str,
        default=None,
        help="Directory where to find a CTranslate Whisper model (e.g. fine-tuned model)",
    )

    # Whisper-ctranslate2 specific parameters
    parser.add_argument(
        "--print-colors",
        type=str2bool,
        default=False,
        help="Print the transcribed text using an experimental color coding strategy to highlight words with high or "
             "low confidence",
    )

    return parser.parse_args().__dict__


def main():
    args = read_command_line()
    output_dir: str = args.pop("output_dir")
    output_format: str = args.pop("output_format")
    os.makedirs(output_dir, exist_ok=True)
    model: str = args.pop("model")
    threads: int = args.pop("threads")
    language: str = args.pop("language")
    task: str = args.pop("task")
    device: str = args.pop("device")
    compute_type: str = args.pop("compute_type")
    verbose: bool = args.pop("verbose")
    model_directory: str = args.pop("model_directory")
    cache_directory: str = args.pop("model_dir")
    device_index: Union[int, List[int]] = args.pop("device_index")

    temperature = args.pop("temperature")
    if (increment := args.pop("temperature_increment_on_fallback")) is not None:
        temperature = tuple(np.arange(temperature, 1.0 + 1e-6, increment))
    else:
        temperature = [temperature]

    language = _from_language_to_iso_code(language)

    if (
            not model_directory
            and model.endswith(".en")
            and language not in {"en", "English"}
    ):
        if language is not None:
            warnings.warn(
                f"{model} is an English-only model but receipted '{language}'; using English instead."
            )
        language = "en"

    if model_directory:
        model_filename = os.path.join(model_directory, "model.bin")
        if not os.path.exists(model_filename):
            raise RuntimeError(f"Model file '{model_filename}' does not exists")
        model_dir = model_directory
    else:
        model_dir = model

    main_task = MainTask(
        beam_size=args.pop("beam_size"),
        best_of=args.pop("best_of"),
        patience=args.pop("patience"),
        length_penalty=args.pop("length_penalty"),
        log_prob_threshold=args.pop("logprob_threshold"),
        no_speech_threshold=args.pop("no_speech_threshold"),
        compression_ratio_threshold=args.pop("compression_ratio_threshold"),
        condition_on_previous_text=args.pop("condition_on_previous_text"),
        temperature=temperature,
        initial_prompt=args.pop("initial_prompt"),
        suppress_tokens=args.pop("suppress_tokens"),
        word_timestamps=args.pop("word_timestamps"),
        print_colors=args.pop("print_colors"),
        verbose=verbose
    )
    for audio_path in args.pop("audio"):
        main_task.tasks(
            audio_path,
            model_dir,
            output_dir,
            output_format,
            task,
            language,
            threads,
            device,
            device_index,
            compute_type)


if __name__ == "__main__":
    main()
