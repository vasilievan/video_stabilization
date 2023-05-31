import torch

from .matching import Matching
from .utils import frame2tensor


class MatchMaker:
    torch.set_grad_enabled(False)

    device: str
    config: dict
    matching: Matching

    def __init__(self, video_type: str):
        self.device = 'cpu'
        print("Device used: %s" % self.device)
        self.config = {
            'superpoint': {
                'nms_radius': 4,
                'keypoint_threshold': 0.005,
                'max_keypoints': 1024
            },
            'superglue': {
                'weights': video_type,
                'sinkhorn_iterations': 20,
                'match_threshold': 0.2,
            }
        }
        self.matching = Matching(self.config).eval().to(self.device)

    def extract_feature_points(self, previous_gray, current_gray):
        inp_previous = frame2tensor(previous_gray, self.device)
        inp_current = frame2tensor(current_gray, self.device)
        pred = self.matching({'image0': inp_previous, 'image1': inp_current})
        pred = {k: v[0].detach().numpy() for k, v in pred.items()}
        kpts0, kpts1 = pred['keypoints0'], pred['keypoints1']
        matches, conf = pred['matches0'], pred['matching_scores0']
        out_matches = {'keypoints0': kpts0, 'keypoints1': kpts1, 'matches': matches, 'match_confidence': conf}
        return out_matches
