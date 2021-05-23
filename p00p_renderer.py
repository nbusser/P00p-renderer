import sys
import json
from concurrent.futures import ThreadPoolExecutor

import project
import sentence_mixing.sentence_mixer as sm
from sentence_mixing.video_creator.video import create_video_file
from sentence_mixing.video_creator.download import dl_video

if __name__ == "__main__":
    path = sys.argv[1]
    config_path = sys.argv[2]

    with open(config_path) as f:
        config = json.load(f)
    if "NODES" in config:
        sm.logic.parameters.NODES = config["NODES"]

    sm.prepare_sm_config_dict(config)

    p = project.load_project(path)

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

    export_filename = "out.mp4"
    phonems = []
    for segment in p.ordered_segments:
        phonems.extend(segment.combo.get_audio_phonems())

    create_video_file(phonems, export_filename)
