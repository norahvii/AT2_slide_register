import math
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


def show_images(images, titles, max_size, columns=4):
    num_images = len(images)
    rows = math.ceil(num_images / columns)
    fig, axes = plt.subplots(rows, columns, figsize=(max_size * columns / 100, max_size * rows / 100))
    axes = axes.flatten()  # Flatten the axes array for easier indexing
    font = FontProperties(weight='bold', size='x-large')

    for i, image in enumerate(images):
        width, height = image.shape[1], image.shape[0]
        aspect_ratio = width / height
        if width > height:
            new_width = max_size
            new_height = int(max_size / aspect_ratio)
        else:
            new_height = max_size
            new_width = int(max_size * aspect_ratio)
        # Convert image to grayscale if it has only one channel
        if len(image.shape) == 2:
            image = np.dstack((image,) * 3)
        axes[i].imshow(image)
        axes[i].axis('off')
        if titles is not None:
            axes[i].set_title(titles[i], fontproperties=font)
    # Hide empty subplots
    for j in range(num_images, len(axes)):
        axes[j].axis('off')
    plt.tight_layout()  # Adjust spacing between subplots
    plt.show()



