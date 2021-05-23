#!/usr/bin/env python3o

import argparse
import sys
import json
from concurrent.futures import ThreadPoolExecutor

import project
import sentence_mixing.sentence_mixer as sm
from sentence_mixing.video_creator.video import create_video_file
from sentence_mixing.video_creator.download import dl_video

DEFAULT_OUTPUT_FILE = "output.mp4"

DESCRIPTION = "Simple tool to render a p00p project into a video"

PROJECT_PATH_HELP = "path to the p00p project file"
CONFIG_PATH_HELP = "path to the json config file"
OUTPUT_FILE_HELP = f"path to the output file (default: {DEFAULT_OUTPUT_FILE})"
TIMESTAMP_OUTPUT_FORMAT_HELP = "determines if the output format should be ffmpeg timestamp list. If this option is activated, output file option will be ignored"

def main(p00p_path, config_path, output_file, timestamp_output_format):

    with open(config_path) as f:
        config = json.load(f)
    if "NODES" in config:
        sm.logic.parameters.NODES = config["NODES"]

    sm.prepare_sm_config_dict(config)

    p = project.load_project(p00p_path)

    urls = p.urls[0]
    vid_paths = list(map(dl_video, urls))
    videos = sm.get_videos(urls, p.seed)

    for video, path in zip(videos, vid_paths):
        n = len(video._base_path)
        assert path[:n] == video._base_path
        video.extension = path[n + 1 :]

    print("Processing segments")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(combo.compute(videos)) for combo in p.ordered_segments]

        while len(futures) > 0:
            i = 0
            while i < len(futures):
                if futures[i].done():
                    n_finished = len(p.ordered_segments) - (len(futures) - 1)
                    print("Segment {}/{} computed".format(n_finished, len(p.ordered_segments)))
                    futures.pop(i)
                else:
                    i += 1

    print("Segment processing done !")
    print("Exporting video")

    phonems = []
    for segment in p.ordered_segments:
        phonems.extend(segment.combo.get_audio_phonems())

    create_video_file(phonems, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "p00p_path",
        metavar="PROJECT_PATH",
        action="store",
        help=PROJECT_PATH_HELP,
    )
    parser.add_argument(
        "config_path",
        metavar="CONFIG_PATH",
        action="store",
        help=CONFIG_PATH_HELP,
    )
    parser.add_argument(
        "-o",
        "--output_file",
        default=DEFAULT_OUTPUT_FILE,
        help=OUTPUT_FILE_HELP,
    )
    parser.add_argument(
        "-t",
        "--timestamp",
        dest="timestamp_output_format",
        action="store_true",
        default=False,
        help=TIMESTAMP_OUTPUT_FORMAT_HELP,
    )

    args = parser.parse_args()

    main(args.p00p_path, args.config_path, args.output_file, args.timestamp_output_format)
