
def create_ffmpeg_command(total_phonems):
    videos = list({phonem.word.sentence.video for phonem in total_phonems})
    index_videos = {v: i for i, v in enumerate(videos)}

    clips = [f"[{index_videos[p.word.sentence.video]}:v]trim={p.start}:{p.end},setpts=PTS-STARTPTS[{i}p]; [{index_videos[p.word.sentence.video]}:a]atrim={p.start}:{p.end},asetpts=PTS-STARTPTS[{i}a]" for i, p in enumerate(total_phonems)]

    paths = "-i ".join([f'"{v._get_video_path()}"' for v in videos])
    print(f'ffmpeg -i {paths} -filter_complex "{"; ".join(clips)};{"".join(["["+str(i)+"p]" for i, _ in enumerate(total_phonems)])}concat=n={len(total_phonems)}:v=1:a=0[v]; {"".join(["["+str(i)+"a]" for i, _ in enumerate(total_phonems)])}concat=n={len(total_phonems)}:v=0:a=1[a]" -map "[a]" -map "[v]" -an -crf 17 output.mp4')