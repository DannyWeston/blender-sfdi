import argparse

from sfdi.definitions import FRINGES_DIR

def handle_args():
    parser = argparse.ArgumentParser()

    # By default use 3 images with names fringe_<0-2>.jpg
    parser.add_argument("--fringes", nargs='+', type=str,
        default=[f'{FRINGES_DIR}/fringes_{i}.jpg' for i in range(3)],
        help="Path to the fringe images to be displayed by the projector")

    parser.add_argument("--runs", type=int, default=1,
        help="How many times to collect a sample for each projection image")

    parser.add_argument("--camera", type=str, default='/dev/video0',
        help="Path to the camera device to use")

    parser.add_argument("--debug", type=bool, default=False,
        help="Toggle debug mode")
    
    parser.add_argument("--interactive", type=bool, default=False,
        help="Toggle interactive console mode (will ignore runs flag)")
    
    parser.add_argument("--refr_index", type=float, default=1.43,
        help="Refractive index to use")

    parser.add_argument("--mu_a", type=float, default=0.018,
        help="TODO: Write help")
    
    parser.add_argument("--mu_sp", type=float, default=0.77,
        help="TODO: Write help")

    args = vars(parser.parse_args())

    return args