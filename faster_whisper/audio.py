"""We use the PyAV library to decode the audio: https://github.com/PyAV-Org/PyAV

The advantage of PyAV is that it bundles the FFmpeg libraries so there is no additional
system dependencies. FFmpeg does not need to be installed on the system.

However, the API is quite low-level so we need to manipulate audio frames directly.
"""

# import io
# import itertools
from typing import BinaryIO, Union

import ffmpeg
# import av
import numpy as np


def decode_audio(input_file: Union[str, BinaryIO], sampling_rate: int = 16000):
    """Decodes the audio.

    Args:
      input_file: Path to the input file or a file-like object.
      sampling_rate: Resample the audio to this sample rate.

    Returns:
      A float32 Numpy array.
    """
    # resampler = av.audio.resampler.AudioResampler(
    #     format="s16",
    #     layout="mono",
    #     rate=sampling_rate,
    # )
    #
    # raw_buffer = io.BytesIO()
    # dtype = None
    #
    # with av.open(input_file, metadata_errors="ignore") as container:
    #     frames = container.decode(audio=0)
    #     frames = _ignore_invalid_frames(frames)
    #     frames = _group_frames(frames, 500000)
    #     frames = _resample_frames(frames, resampler)
    #
    #     for frame in frames:
    #         array = frame.to_ndarray()
    #         dtype = array.dtype
    #         raw_buffer.write(array)
    #
    # audio = np.frombuffer(raw_buffer.getbuffer(), dtype=dtype)
    #
    # # Convert s16 back to f32.
    # return audio.astype(np.float32) / 32768.0
    """
    Open an audio file and read as mono waveform, resampling as necessary

    Parameters
    ----------
    file: str
        The audio file to open

    sr: int
        The sample rate to resample the audio if necessary

    Returns
    -------
    A NumPy array containing the audio waveform, in float32 dtype.
    """
    try:
        # This launches a subprocess to decode audio while down-mixing and resampling as necessary.
        # Requires the ffmpeg CLI and `ffmpeg-python` package to be installed.
        out, _ = (
            ffmpeg.input(input_file, threads=0)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sampling_rate)
            .run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

# def _ignore_invalid_frames(frames):
#     iterator = iter(frames)
#
#     while True:
#         try:
#             yield next(iterator)
#         except StopIteration:
#             break
#         except av.error.InvalidDataError:
#             continue


# def _group_frames(frames, num_samples=None):
#     fifo = av.audio.fifo.AudioFifo()
#
#     for frame in frames:
#         frame.pts = None  # Ignore timestamp check.
#         fifo.write(frame)
#
#         if num_samples is not None and fifo.samples >= num_samples:
#             yield fifo.read()
#
#     if fifo.samples > 0:
#         yield fifo.read()


# def _resample_frames(frames, resampler):
#     # Add None to flush the resampler.
#     for frame in itertools.chain(frames, [None]):
#         yield from resampler.resample(frame)
