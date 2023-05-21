import sys

from smtp import Smtp


if __name__ == '__main__':
    Smtp().send(sys.argv)
