import pickle
from copy import copy
import struct
import sentence_mixing.sentence_mixer as sm

FORMAT_VERSION = 2
MAGIC_NUMBER = 0x70303070


def load_project(project_path):
    """Loads project from p00p file"""
    with open(project_path, "rb") as project_file:
        # Read and check the header
        magic = struct.unpack('>I', project_file.read(4))[0]
        if magic != MAGIC_NUMBER:
            raise EnvironmentError("Bad file format")

        # Read the version
        version = struct.unpack('>I', project_file.read(4))[0]

        if version > FORMAT_VERSION:
            raise EnvironmentError("File too new for this version.")

        # Read the data size
        data_size = struct.unpack('>I', project_file.read(4))[0]

        # Read the data
        data = project_file.read(data_size)

    return Project.from_JSON_serializable(pickle.loads(data))


class ChosenCombo:
    def __init__(self, sentence, index):
        self.sentence = sentence
        self.index = index
        self.combo = None

    def compute(self, videos):
        self.combo = sm.process_sm(self.sentence, videos)[self.index]

    def from_JSON_serializable(json_serializable):
        return ChosenCombo(json_serializable["sentence"], json_serializable["index"])


class Project:
    def __init__(self, seed, urls, ordered_segments):
        self.seed = seed
        self.urls = urls
        self.ordered_segments = ordered_segments

    def from_JSON_serializable(schema):
        ordered = [ChosenCombo.from_JSON_serializable(c) for c in schema["ordered_segments"]]
        return Project(schema["seed"], schema["urls"], ordered)
