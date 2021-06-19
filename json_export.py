import os
import json

def create_json(total_phonems):
    videos = list({phonem.word.sentence.video for phonem in total_phonems})
    index_videos = {v: i for i, v in enumerate(videos)}

    result = dict()
    result["sources"] = list(map(lambda v: os.path.abspath(v._get_video_path()), videos))

    result["timeline"] = [
        {"src": index_videos[p.word.sentence.video], "start": p.start, "end": p.end}
        for p in total_phonems
    ]

    print(json.dumps(result))
