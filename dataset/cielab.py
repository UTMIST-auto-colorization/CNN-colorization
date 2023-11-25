import torch
import joblib
import numpy as np

RESOURCES_DIR = "resources/"
BUCKETS_PATH = RESOURCES_DIR + "buckets_313.npy"
BUCKETS_KNN_PATH = RESOURCES_DIR + "buckets_knn.joblib"

class CIELabConversion():
    def __init__(
        self,
        buckets_path: str = BUCKETS_PATH,
        buckets_knn_path: str = BUCKETS_KNN_PATH
    ) -> None:
        """
        Instantiates class for converting CIELab ab-values to Buckets.

        Args:
            buckets_path (str): Path to .npy file containing all the quantized ab-value
                buckets.
            buckets_knn_path (str): Path to .joblib file containing the Nearest-Neighbor
                classifier for finding the closest bucket to an ab-value.

        Attributes:
            buckets (np.ndarray): NumPy array containing all the quantized ab-value
                buckets.
            buckets_knn (sklearn.neighbors.KNeighborsClassifier): Nearest-Neighbor (k = 1)
                classifier for finding the closest bucket to an ab-value.
            ab2bucket (dict[tuple[int, int], int]): Dict for converting a quantized ab-value
                to corresponding bucket index.
            bucket2ab (dict[int, tuple[int, int]]): Dict for converting a bucket index to
                corresponding ab-value.
        """
        self.buckets = np.load(buckets_path)
        self.buckets_knn = joblib.load(buckets_knn_path)
        self.ab2bucket = {tuple(self.buckets[i]): i+1 for i in range(len(self.buckets))}
        self.bucket2ab = {i+1: tuple(self.buckets[i]) for i in range(len(self.buckets))}
        
    def get_image_ab_buckets(self, image_lab: np.ndarray) -> np.ndarray:
        """
        Get bucketed ab-values from Lab image.
        """
        image_ab = image_lab[:, :, 1:]
        orig_ab_shape = image_ab.shape

        image_ab = image_ab.reshape(-1, 2)
        image_ab = self.buckets_knn.predict(image_ab)
        image_ab = image_ab.reshape((orig_ab_shape[0], orig_ab_shape[1]))

        return image_ab

    def convert_buckets_to_ab(self, image_buckets: np.ndarray) -> np.ndarray:
        """
        Get ab-values from bucketed image.
        """
        converted_image_ab = []
        for row in image_buckets:
            new_row = []
            for i in row:
                new_row.append(self.bucket2ab[i])
            converted_image_ab.append(new_row)

        converted_image_ab = np.array(converted_image_ab)

        return converted_image_ab

    def batch_convert_buckets_to_ab(self, batch):
        converted_batch = []
        for image in batch:
            converted_image = self.convert_buckets_to_ab(image)
            converted_batch.append(converted_image)
        return torch.stack(converted_batch)