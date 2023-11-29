import os


class TotalStatus():
    def __init__(self):
        pass

    def stats(self):

        dir_list = "./Files/Error", "./Files/InProcess", "./Files/NewFiles"

        for d in dir_list:

            count = 0

            for subdirectory in os.listdir(d):
                count = count + 1

            print(f"{count} in {d}")
