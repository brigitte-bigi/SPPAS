import queue
import pyaudio

# ---------------------------------------------------------------------------


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks.

    This class manages the audio stream, captures chunks of audio data,
    and yields them as a generator. It is designed to be used within a
    'with' statement to ensure proper resource management.

    The loop inside the `generator()` method runs indefinitely, receiving and
    yielding audio data as long as the microphone stream is active. It stops
    only when the stream is closed, which happens when the `__exit__` method
    is called (i.e., when the `with` statement block ends or when manually
    stopped). After the stream is closed, the generator terminates and no
    more audio data is yielded.

    :example:
    >>> with MicrophoneStream(rate=16000, chunck=1024) as stream:
    >>>     for audio_chunk in stream.generator():
    >>>         print(f"Received audio chunk: {len(audio_chunk)} bytes")
    >>>         # Process the audio chunk as it is received.
    >>>         process_audio(audio_chunk)

    """

    def __init__(self, rate: int, chunk: int):
        """Initialize the microphone stream.

        Initializes the audio stream with the given rate and chunk size.
        Sets up a thread-safe queue to store audio data from the stream.

        :param rate: (int) The sample rate of the audio stream (samples per second).
        :param chunk: (int) The number of frames per buffer (size of each chunk).

        """
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()  # Thread-safe buffer to store audio data
        self.closed = True

    # -----------------------------------------------------------------------

    def generator(self) -> bytes:
        """Yield audio chunks from the microphone stream.

        This method is a generator that yields chunks of audio data as they
        are collected from the stream. It continues to yield chunks until the
        stream is closed. If no more chunks are available, it terminates.

        :yield: (bytes) The concatenated audio data chunks from the stream.

        """
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

    # -----------------------------------------------------------------------

    def _fill_buffer(self, in_data: bytes, frame_count: int, time_info, status_flags) -> tuple:
        """Continuously collect data from the audio stream into the buffer.

        This method is called by the audio stream callback function to fill
        the buffer with audio data as it is being captured.

        :param in_data: (bytes) Audio data from the stream.
        :param frame_count: (int) The number of frames in the current chunk.
        :param time_info: (dict) Time-related information from the audio stream.
        :param status_flags: (int) Status flags from the audio stream.
        :return: (None, pyaudio.paContinue) To continue the stream.

        """
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __enter__(self) -> 'MicrophoneStream':
        """Start the microphone stream.

        This method initializes the audio interface and stream, then starts
        streaming audio data. It is designed to be used in a 'with' statement
        to automatically handle resource management.

        :return: (MicrophoneStream) The current instance of the MicrophoneStream.

        """
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,  # Mono audio channel
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )

        self.closed = False
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, type, value, traceback) -> None:
        """Stop and close the microphone stream when exiting the 'with' statement.

        This method ensures the audio stream is properly stopped and closed,
        and the audio interface is terminated to release resources.

        :param type: The exception type (if any).
        :param value: The exception value (if any).
        :param traceback: The traceback object (if any).

        """
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)  # Signal to terminate the generator
        self._audio_interface.terminate()
