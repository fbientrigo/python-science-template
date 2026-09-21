import json

from science_project import summarize

if __name__ == "__main__":
    print(json.dumps(summarize([1.0, 2.0, 3.0]), sort_keys=True))
