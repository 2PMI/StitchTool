import cv2
import numpy as np


# @jit(nopython=True)
def nonLocalMeans(noisy, params=[20, 6, 14], verbose=True):
    """
    Performs the non-local-means algorithm given a noisy image.
    params is a tuple with:
    params = (bigWindowSize, smallWindowSize, h)
    Please keep bigWindowSize and smallWindowSize as even numbers
    """

    [bigWindowSize, smallWindowSize, h] = params
    padwidth = bigWindowSize // 2
    image = noisy.copy()

    # The next few lines creates a padded image that reflects the border so that the big window can be accomodated through the loop
    paddedImage = np.zeros(
        (image.shape[0] + bigWindowSize, image.shape[1] + bigWindowSize)
    )
    paddedImage = paddedImage.astype(np.uint8)
    paddedImage[
        padwidth : padwidth + image.shape[0], padwidth : padwidth + image.shape[1]
    ] = image
    paddedImage[padwidth : padwidth + image.shape[0], 0:padwidth] = np.fliplr(
        image[:, 0:padwidth]
    )
    paddedImage[
        padwidth : padwidth + image.shape[0],
        image.shape[1] + padwidth : image.shape[1] + 2 * padwidth,
    ] = np.fliplr(image[:, image.shape[1] - padwidth : image.shape[1]])
    paddedImage[0:padwidth, :] = np.flipud(paddedImage[padwidth : 2 * padwidth, :])
    paddedImage[
        padwidth + image.shape[0] : 2 * padwidth + image.shape[0], :
    ] = np.flipud(
        paddedImage[
            paddedImage.shape[0] - 2 * padwidth : paddedImage.shape[0] - padwidth, :
        ]
    )

    iterator = 0
    totalIterations = (
        image.shape[1] * image.shape[0] * (bigWindowSize - smallWindowSize) ** 2
    )

    if verbose:
        print("TOTAL ITERATIONS = ", totalIterations)

    outputImage = paddedImage.copy()

    smallhalfwidth = smallWindowSize // 2

    # For each pixel in the actual image, find a area around the pixel that needs to be compared
    for imageX in range(padwidth, padwidth + image.shape[1]):
        for imageY in range(padwidth, padwidth + image.shape[0]):

            bWinX = imageX - padwidth
            bWinY = imageY - padwidth

            # comparison neighbourhood
            compNbhd = paddedImage[
                imageY - smallhalfwidth : imageY + smallhalfwidth + 1,
                imageX - smallhalfwidth : imageX + smallhalfwidth + 1,
            ]

            pixelColor = 0
            totalWeight = 0

            # For each comparison neighbourhood, search for all small windows within a large box, and compute their weights
            for sWinX in range(bWinX, bWinX + bigWindowSize - smallWindowSize, 1):
                for sWinY in range(bWinY, bWinY + bigWindowSize - smallWindowSize, 1):
                    # find the small box
                    smallNbhd = paddedImage[
                        sWinY : sWinY + smallWindowSize + 1,
                        sWinX : sWinX + smallWindowSize + 1,
                    ]
                    euclideanDistance = np.sqrt(np.sum(np.square(smallNbhd - compNbhd)))
                    # weight is computed as a weighted softmax over the euclidean distances
                    weight = np.exp(-euclideanDistance / h)
                    totalWeight += weight
                    pixelColor += (
                        weight
                        * paddedImage[sWinY + smallhalfwidth, sWinX + smallhalfwidth]
                    )
                    iterator += 1

                    if verbose:
                        percentComplete = iterator * 100 / totalIterations
                    if percentComplete % 5 == 0:
                        print("% COMPLETE = ", percentComplete)

                pixelColor /= totalWeight
                outputImage[imageY, imageX] = pixelColor

    return outputImage[
        padwidth : padwidth + image.shape[0], padwidth : padwidth + image.shape[1]
    ]
