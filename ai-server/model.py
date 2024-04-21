#!/usr/bin/env python3

import torchvision

def main():
    # just put everything in a loop
    while True:
        filename = input()
        vframes, _, _ = torchvision.io.read_video(filename)
        # TODO: The actual model call
        print(f"Got tensor with shape {vframes.shape}")

if __name__ == "__main__":
    main()
