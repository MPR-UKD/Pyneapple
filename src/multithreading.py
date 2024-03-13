import src.istarmap  # import to apply patch
from typing import Callable
from functools import partial
from multiprocessing import Pool
import numpy as np


def multithreader(
    func: Callable | partial,
    arg_list: zip | tuple,  # tuple for @JJ segmentation wise?
    n_pools: int | None = None,
) -> list:
    """
    Handles multithreading for different Functions.

    Will take a fully partialized function and a zipped list io arguments containing indexes for array positions
    and process them ether sequential or parallel. The results of each call are returned as a list of tuples.

    Attributes:
    ----------
    func :
        Callable | partial containing the function to process with only the indices and the array missing.
    arg_list :
        zip containing data to process zip(position, array)
    n_pools:
        Number of threads to use for multiprocessing. If ether 0 or None is given no threads will be used.
    """

    def starmap_handler(
        function: Callable, arguments_list: zip, number_pools: int
    ) -> list:
        """
        Handles multithreading for different Functions.

        Will tak ea a partial function and a zipped list to run it in parallel threats.

        Args:
            function:
            arguments_list:
            number_pools:

        Returns:

        """
        if number_pools != 0:
            with Pool(number_pools) as pool:
                results_list = pool.starmap(function, arguments_list)

                # https://stackoverflow.com/questions/57354700/starmap-combined-with-tqdm
                # results_list = list()
                # n_args = list(zip(*arguments_list))  # total=len(n_args[0])
                # results_list = [
                #     result
                #     for result in tqdm(
                #         pool.istarmap(function, arguments_list), total=len(n_args[0])
                #     )
                # ]

        return results_list

    results = list()
    # Perform multithreading accordingly
    if n_pools:
        results = starmap_handler(func, arg_list, n_pools)
    else:
        for element in arg_list:
            results.append(func(*element))
    return results


def sort_interpolated_array(results: list, array: np.ndarray) -> np.ndarray:
    """
    Sort results interpolated image planes to array of desired shape.

    Args:
        results: List of tuples containing the index and the processed data.
        array: New array to cast into.

    Returns:
        array: With sorted results.
    """
    for element in results:
        array[:, :, *element[0]] = element[1]
    return array


def sort_fit_array(results: list, array: np.ndarray) -> np.ndarray:
    """
    Sort results from fitted pixels to array of desired shape.

    Args:
        results: List of tuples containing the index and the processed data.
        array: New array to cast into.

    Returns:
        array: With sorted results.
    """
    for element in results:
        array[element[0]] = element[1]
    return array
