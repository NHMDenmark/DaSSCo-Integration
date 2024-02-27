import time
import sys

if __name__ == "__main__":
        if len(sys.argv) < 2:
                print("too few")
                sys.exit(1)

        v = sys.argv[1]
        time.sleep(2)
        print(f"{v}, 2nd done")