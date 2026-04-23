from fastrtc import Stream #type:ignore
import numpy as np #type:ignore


def flip_vertically(image):
    return np.flip(image, axis=0)


stream = Stream(
    handler=flip_vertically,
    modality="video",
    mode="send",
)