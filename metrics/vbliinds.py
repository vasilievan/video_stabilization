from skvideo.io import vread
from skvideo.measure import videobliinds_features
import numpy as np
import sys
import os.path


def count_videobliinds(path):
    video = vread(path, outputdict={"-pix_fmt": "gray"})
    result = videobliinds_features(video)
    np.set_printoptions(precision=3)
    np.set_printoptions(suppress=True, formatter={'float_kind': '{:.3f}'.format})
    formatted_result = np.array(result)
    return formatted_result[:36], formatted_result[36], formatted_result[37:39], formatted_result[39:44], \
           formatted_result[44], formatted_result[45]


def count_united():
    if len(sys.argv) != 3:
        print("Incorrect arguments!")
        return
    if not os.path.isfile(sys.argv[1]):
        print("Incorrect arguments!")
        return
    if not os.path.isfile(sys.argv[2]):
        print("Incorrect arguments!")
        return
    reference = count_videobliinds(sys.argv[1])
    stabilized = count_videobliinds(sys.argv[2])
    gammas_counter = 0
    niqe_counter = 0
    dc_counter = 0
    naturalness_stat_counter = 0
    coherence_counter = 0
    glob_motion_counter = 0
    for i in range(36):
        if abs(reference[i]) > abs(stabilized[i]):
            gammas_counter += 1
    if reference[36] > stabilized[36]:
        niqe_counter += 1
    for i in range(2):
        if reference[i + 37] > stabilized[i + 37]:
            dc_counter += 1
    for i in range(5):
        if reference[i + 39] > stabilized[i + 39]:
            naturalness_stat_counter += 1
    if reference[44] < stabilized[44]:
        coherence_counter += 1
    if abs(1 - reference[45]) > abs(1 - stabilized[45]):
        glob_motion_counter += 1
    return 0.5 * gammas_counter + \
           0.05 * niqe_counter + \
           0.2 * dc_counter + \
           0.05 * naturalness_stat_counter + \
           0.1 * coherence_counter + \
           0.1 * glob_motion_counter


if __name__ == "__main__":
    metrics = count_united()
    print("Metrics: %f" % metrics)
