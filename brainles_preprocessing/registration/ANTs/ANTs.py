# TODO add typing and docs
import os
import shutil

import ants
from auxiliary.turbopath import turbopath

from brainles_preprocessing.registration.registrator import Registrator


class ANTsRegistrator(Registrator):
    def __init__(
        self,
        registration_params: dict = None,
        transformation_params: dict = None,
    ):
        """
        Initialize an ANTsRegistrator instance.

        Parameters:
        - registration_params (dict, optional): Dictionary of parameters for the registration method.
          Defaults to None, which implies using default registration parameters with a rigid transformation.
        - transformation_params (dict, optional): Dictionary of parameters for the transformation method.
          Defaults to an empty dictionary.

        The registration_params dictionary may include the following keys:
        - type_of_transform (str, optional): Type of transformation to use (default is "Rigid").

        Example:
        >>> reg_params = {'type_of_transform': 'Affine', 'reg_iterations': (30, 20, 10)}
        >>> transform_params = {'interpolator': 'linear', 'imagetype': 1}
        >>> registrator = ANTsRegistrator(registration_params=reg_params, transformation_params=transform_params)
        """
        # Set default registration parameters
        default_registration_params = {"type_of_transform": "Rigid"}
        self.registration_params = registration_params or default_registration_params

        # Set default transformation parameters
        self.transformation_params = transformation_params or {}

    def register(
        self,
        fixed_image_path: str,
        moving_image_path: str,
        transformed_image_path: str,
        matrix_path: str,
        log_file_path: str,
        **kwargs,
    ) -> None:
        """
        Register images using ANTs.

        Args:
            fixed_image_path (str): Path to the fixed image.
            moving_image_path (str): Path to the moving image.
            transformed_image_path (str): Path to the transformed image (output).
            matrix_path (str): Path to the transformation matrix (output).
            log_file_path (str): Path to the log file.
            **kwargs: Additional registration parameters to update the instantiated defaults.
        """
        # we update the transformation parameters with the provided kwargs
        registration_kwargs = {**self.registration_params, **kwargs}
        transformed_image_path = turbopath(transformed_image_path)

        matrix_path = turbopath(matrix_path)
        if matrix_path.suffix != ".mat":
            matrix_path = matrix_path.with_suffix(".mat")

        fixed_image = ants.image_read(fixed_image_path)
        moving_image = ants.image_read(moving_image_path)
        registration_result = ants.registration(
            fixed=fixed_image,
            moving=moving_image,
            **registration_kwargs,
        )
        transformed_image = registration_result["warpedmovout"]
        os.makedirs(transformed_image_path.parent, exist_ok=True)
        ants.image_write(transformed_image, transformed_image_path)
        os.makedirs(matrix_path.parent, exist_ok=True)
        shutil.copyfile(registration_result["fwdtransforms"][0], matrix_path)
        # TODO logging

    def transform(
        self,
        fixed_image_path: str,
        moving_image_path: str,
        transformed_image_path: str,
        matrix_path: str,
        log_file_path: str,
        **kwargs,
    ) -> None:
        """
        Apply a transformation using ANTs.

        Args:
            fixed_image_path (str): Path to the fixed image.
            moving_image_path (str): Path to the moving image.
            transformed_image_path (str): Path to the transformed image (output).
            matrix_path (str): Path to the transformation matrix.
            log_file_path (str): Path to the log file.
            **kwargs: Additional transformation parameters to update the instantiated defaults.
        """
        # we update the transformation parameters with the provided kwargs
        transform_kwargs = {**self.transformation_params, **kwargs}
        fixed_image = ants.image_read(fixed_image_path)
        moving_image = ants.image_read(moving_image_path)
        transformed_image_path = turbopath(transformed_image_path)
        os.makedirs(transformed_image_path.parent, exist_ok=True)

        matrix_path = turbopath(matrix_path)
        if matrix_path.suffix != ".mat":
            matrix_path = matrix_path.with_suffix(".mat")
        transformed_image = ants.apply_transforms(
            fixed=fixed_image,
            moving=moving_image,
            transformlist=[matrix_path],
            **transform_kwargs,
        )
        ants.image_write(transformed_image, transformed_image_path)
        # TODO logging


if __name__ == "__main__":
    # TODO move this into unit tests
    reg = ANTsRegistrator()

    reg.register(
        fixed_image_path="example/example_data/TCGA-DU-7294/AX_T1_POST_GD_FLAIR_TCGA-DU-7294_TCGA-DU-7294_GE_TCGA-DU-7294_AX_T1_POST_GD_FLAIR_RM_13_t1c.nii.gz",
        moving_image_path="example/example_data/TCGA-DU-7294/AX_T2_FR-FSE_RF2_150_TCGA-DU-7294_TCGA-DU-7294_GE_TCGA-DU-7294_AX_T2_FR-FSE_RF2_150_RM_4_t2.nii.gz",
        transformed_image_path="example/example_ants/transformed_image.nii.gz",
        matrix_path="example/example_ants_matrix/matrix",
        log_file_path="example/example_ants/log.txt",
    )

    reg.transform(
        fixed_image_path="example/example_data/TCGA-DU-7294/AX_T1_POST_GD_FLAIR_TCGA-DU-7294_TCGA-DU-7294_GE_TCGA-DU-7294_AX_T1_POST_GD_FLAIR_RM_13_t1c.nii.gz",
        moving_image_path="example/example_data/OtherEXampleFromTCIA/T1_AX_OtherEXampleTCIA_TCGA-FG-6692_Si_TCGA-FG-6692_T1_AX_SE_10_se2d1_t1.nii.gz",
        transformed_image_path="example/example_ants_transformed/transformed_image.nii.gz",
        matrix_path="example/example_ants_matrix/matrix.mat",
        log_file_path="example/example_ants/log.txt",
    )
