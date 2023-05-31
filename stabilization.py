import math
import cv2
import numpy as np
from feature_detection.match_pairs import MatchMaker


class Stabilization:
    max_corners = 800
    min_distance = 10
    quality_level = 0.01
    radius = 7

    def __init__(self,
                 unstabilized: str,
                 stabilized: str,
                 radius: int = 7,
                 match_threshold: float = 0.95,
                 door: str = 'indoor'
                 ):
        self.radius = radius
        self.match_threshold = match_threshold
        self.unstabilized = unstabilized
        if stabilized == "":
            split = unstabilized.split('.')
            self.stabilized = split[0] + "_stabilized" + split[1]
        else:
            self.stabilized = stabilized
        if door == 'indoor':
            self.match_maker = MatchMaker('indoor')
        elif door == 'outdoor':
            self.match_maker = MatchMaker('outdoor')
        else:
            self.match_maker = None

    def stabilize_video_standard(self):
        unstabilized = cv2.VideoCapture(self.unstabilized)
        stabilized = cv2.VideoWriter(self.stabilized,
                                     cv2.VideoWriter_fourcc(*'mp4v'),
                                     unstabilized.get(cv2.CAP_PROP_FPS),
                                     (int(unstabilized.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                      int(unstabilized.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                                     )
        ret, previous_frame = unstabilized.read()
        if not ret:
            return
        previous_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
        resize = 0
        transformations = []
        frame_counter = 0
        while unstabilized.isOpened():
            ret, current_frame = unstabilized.read()
            if not ret:
                break
            current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
            previous_features = cv2.goodFeaturesToTrack(previous_gray, self.max_corners, self.quality_level,
                                                        self.min_distance)
            current_features = cv2.goodFeaturesToTrack(current_gray, self.max_corners, self.quality_level,
                                                       self.min_distance)
            pairs, st, err = cv2.calcOpticalFlowPyrLK(previous_gray, current_gray, previous_features, current_features)
            previous_features = previous_features[st==1]
            current_features = current_features[st == 1]
            affine_transformation, _ = cv2.estimateAffine2D(previous_features, current_features)
            if affine_transformation is None:
                if len(transformations) > 0:
                    transformations.append(transformations[-1])
                else:
                    transformations.append([0, 0, 0])
                previous_gray = current_gray
                print("Frame #%d is done." % frame_counter)
                frame_counter += 1
                continue
            dx = affine_transformation[0][2]
            dy = affine_transformation[1][2]
            da = math.atan2(affine_transformation[1][0], affine_transformation[0][0])
            resize_da = 1.0 + abs(math.tan(da) * previous_frame.shape[1] / previous_frame.shape[0])
            resize_dx = 1.0 + 2 * abs(dx) / previous_frame.shape[0]
            resize_dy = 1.0 + 2 * abs(dy) / previous_frame.shape[1]
            current_resize = max(resize_dx, resize_dy, resize_da)
            if current_resize > resize:
                resize = current_resize
            transformations.append([dx, dy, da])
            previous_gray = current_gray
            print("Frame #%d is done." % frame_counter)
            frame_counter += 1
        trajectory = self.accumulate_trajectory(transformations)
        stabilized_trajectory = self.stabilize_trajectory(trajectory)
        smoothed_transformations = self.smooth_transformations(trajectory, stabilized_trajectory)
        unstabilized.set(cv2.CAP_PROP_POS_FRAMES, 0)
        for frame_index in range(len(smoothed_transformations)):
            ret, unstabilized_frame = unstabilized.read()
            if not ret:
                break
            transformation_matrix = self.get_transformation_matrix(smoothed_transformations[frame_index])
            warped = cv2.warpAffine(unstabilized_frame, transformation_matrix,
                                    (unstabilized_frame.shape[1], unstabilized_frame.shape[0]))
            fixed = self.fix_borders(warped, resize)
            stabilized.write(fixed)
        print("Stabilization finished.")
        unstabilized.release()
        stabilized.release()

    def stabilize_video_neural(self):
        unstabilized = cv2.VideoCapture(self.unstabilized)
        stabilized = cv2.VideoWriter(self.stabilized,
                                     cv2.VideoWriter_fourcc(*'mp4v'),
                                     unstabilized.get(cv2.CAP_PROP_FPS),
                                     (int(unstabilized.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                      int(unstabilized.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                                     )
        ret, previous_frame = unstabilized.read()
        if not ret:
            return
        previous_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
        resize = 0
        transformations = []
        frame_counter = 0
        while unstabilized.isOpened():
            ret, current_frame = unstabilized.read()
            if not ret:
                break
            current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
            matches_dictionary = self.match_maker.extract_feature_points(previous_gray, current_gray)
            match_confidence = matches_dictionary['match_confidence']
            matches = matches_dictionary['matches']
            keypoint_previous = matches_dictionary['keypoints0']
            keypoint_current = matches_dictionary['keypoints1']
            keypoint_previous_good = []
            keypoint_current_good = []
            for i in range(len(match_confidence)):
                if match_confidence[i] > self.match_threshold:
                    keypoint_previous_good.append(keypoint_previous[i])
                    keypoint_current_good.append(keypoint_current[matches[i]])
            keypoint_previous_good = np.array(keypoint_previous_good)
            keypoint_current_good = np.array(keypoint_current_good)
            if (len(keypoint_previous_good) > 0) and (len(keypoint_current_good) > 0):
                _, status, _ = cv2.calcOpticalFlowPyrLK(previous_gray,
                                                        current_gray,
                                                        keypoint_previous_good,
                                                        keypoint_current_good)
                keypoint_previous_good = np.delete(keypoint_previous_good, [i for i, x in enumerate(status) if x == 0],
                                                   0)
                keypoint_current_good = np.delete(keypoint_current_good, [i for i, x in enumerate(status) if x == 0], 0)

                if (len(keypoint_current_good) == len(keypoint_previous_good)) and \
                        (len(keypoint_current_good) > 0) and \
                        (len(keypoint_previous_good) > 0):
                    affine_transformation, _ = cv2.estimateAffine2D(keypoint_previous_good, keypoint_current_good)
                else:
                    affine_transformation = None
            else:
                affine_transformation = None
            if affine_transformation is None:
                if len(transformations) > 0:
                    transformations.append(transformations[-1])
                else:
                    transformations.append([0, 0, 0])
                previous_gray = current_gray
                print("Frame #%d is done." % frame_counter)
                frame_counter += 1
                continue
            dx = affine_transformation[0][2]
            dy = affine_transformation[1][2]
            da = math.atan2(affine_transformation[1][0], affine_transformation[0][0])
            resize_da = 1.0 + abs(math.tan(da) * previous_frame.shape[1] / previous_frame.shape[0])
            resize_dx = 1.0 + 2 * abs(dx) / previous_frame.shape[0]
            resize_dy = 1.0 + 2 * abs(dy) / previous_frame.shape[1]
            current_resize = max(resize_dx, resize_dy, resize_da)
            if current_resize > resize:
                resize = current_resize
            transformations.append([dx, dy, da])
            previous_gray = current_gray
            print("Frame #%d is done." % frame_counter)
            frame_counter += 1
        trajectory = self.accumulate_trajectory(transformations)
        stabilized_trajectory = self.stabilize_trajectory(trajectory)
        smoothed_transformations = self.smooth_transformations(trajectory, stabilized_trajectory)
        unstabilized.set(cv2.CAP_PROP_POS_FRAMES, 0)
        for frame_index in range(len(smoothed_transformations)):
            ret, unstabilized_frame = unstabilized.read()
            if not ret:
                break
            transformation_matrix = self.get_transformation_matrix(smoothed_transformations[frame_index])
            warped = cv2.warpAffine(unstabilized_frame, transformation_matrix,
                                    (unstabilized_frame.shape[1], unstabilized_frame.shape[0]))
            fixed = self.fix_borders(warped, resize)
            stabilized.write(fixed)
        print("Stabilization finished.")
        unstabilized.release()
        stabilized.release()

    def stabilize_trajectory(self, trajectory):
        stabilized_trajectory = []
        for outer_index in range(len(trajectory)):
            summarized_x = 0
            summarized_y = 0
            summarized_a = 0
            count = 0
            for inner_index in range(-self.radius, self.radius):
                if (inner_index + outer_index >= 0) and (inner_index + outer_index < len(trajectory)):
                    summarized_x += trajectory[inner_index + outer_index][0]
                    summarized_y += trajectory[inner_index + outer_index][1]
                    summarized_a += trajectory[inner_index + outer_index][2]
                    count += 1
            stabilized_trajectory.append([summarized_x / count, summarized_y / count, summarized_a / count])
        return stabilized_trajectory

    def smooth_transformations(self, trajectory, stabilized_trajectory):
        smoothed_transformations = []
        for i in range(len(trajectory)):
            trajectory_differences_x = stabilized_trajectory[i][0] - trajectory[i][0]
            trajectory_differences_y = stabilized_trajectory[i][1] - trajectory[i][1]
            trajectory_differences_a = stabilized_trajectory[i][2] - trajectory[i][2]
            smoothed_transformations.append(
                [trajectory_differences_x, trajectory_differences_y, trajectory_differences_a])
        return smoothed_transformations

    def get_transformation_matrix(self, transformation):
        matrix = np.zeros((2, 3))
        matrix[0][0] = math.cos(transformation[2])
        matrix[0][1] = -math.sin(transformation[2])
        matrix[1][0] = math.sin(transformation[2])
        matrix[1][1] = math.cos(transformation[2])
        matrix[0][2] = transformation[0]
        matrix[1][2] = transformation[1]
        return matrix

    def fix_borders(self, matrix, resize):
        rotation_matrix = cv2.getRotationMatrix2D((matrix.shape[0] / 2.0, matrix.shape[1] / 2.0), 0, resize)
        warped = cv2.warpAffine(matrix, rotation_matrix, (matrix.shape[1], matrix.shape[0]))
        return warped

    def accumulate_trajectory(self, transformations):
        accumulated_dx = 0
        accumulated_dy = 0
        accumulated_da = 0
        trajectory = []
        for transformation in transformations:
            accumulated_dx += transformation[0]
            accumulated_dy += transformation[1]
            accumulated_da += transformation[2]
            trajectory.append([accumulated_dx, accumulated_dy, accumulated_da])
        return trajectory
