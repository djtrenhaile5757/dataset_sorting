import cv2
import argparse
import os
import json

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", required=True, help="path to pull directory")
ap.add_argument("-e", "--errors", required=True, help="path to errors directory")
ap.add_argument("-k", "--keys", required=True, help="path to key mappings")
ap.add_argument("-s", "--start", required=False, help="optional argument for starting point in image pool")
args = vars(ap.parse_args())


def clean_directory():
    print("[INFO] Cleaning pull directories...")
    for dirpath, _, files in os.walk(args["directory"]):
        for file in files:
            if file == ".DS_Store":
                print("[INFO] Removed .DS_Store file...")
                print()
                os.remove(os.path.join(dirpath, file))


def index_ims(images):
    upper = len(images)
    indexed_images = list()
    index = images[0][0]

    if isinstance(index, str):
        for x in range(0, upper):
            im_path = images[x][0]
            image = images[x][1]
            data = [x, image, im_path]
            indexed_images.append(data)
    elif isinstance(index, int):
        for x in range(0, upper):
            if not images[x][0] == x:
                images[x][0] = x
            indexed_images = images

    return indexed_images


def load_imgs():
    images = list()
    for dirpath, _, files in os.walk(args["directory"]):
        for file in files:
            im_path = os.path.join(dirpath, file)
            image = cv2.imread(im_path)
            data = [im_path, image]
            images.append(data)

    return images


def sort(images):
    im_num = 0
    images = index_ims(images)
    if isinstance(args["start"], str):
        im_num += int(args["start"]) - 1

    while True:
        images = index_ims(images)

        im_max = images[-1][0]
        image = images[im_num][1]
        im_path = images[im_num][2]
        im_name = os.path.basename(im_path)
        name = "(" + str(im_num + 1) + "/" + str(im_max + 1) + ") " + im_name

        if image is None:
            print("[INFO] Image is NoneType; moving to errors directory")
            print()

            os.rename(im_path, os.path.join(args["errors"], im_name))
            images.remove([im_num, image, im_path])

        else:
            resize_ratio = 850
            r = resize_ratio / image.shape[1]
            dim = (resize_ratio, int(image.shape[0] * r))
            resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

            cv2.namedWindow(name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(name, 1000, 600)
            cv2.moveWindow(name, 438, 20)

            cv2.imshow(name, resized)
            k = cv2.waitKey(1) & 0xFF

            if k is not 255:
                process = True
                if k == 96:
                    break
                if k == 32 or k == 52:
                    process = False
                    if im_num == im_max:
                        print("[INFO] End of image pool")
                        print()
                    else:
                        cv2.destroyWindow(name)
                        im_num += 1
                if k == 51:
                    process = False
                    if im_num == 0:
                        print("[INFO] Already at beginning of image pool")
                        print()
                    else:
                        cv2.destroyWindow(name)
                        im_num -= 1

                if process:
                    key = ""
                    with open(args["keys"]) as f:
                        data = json.load(f)
                        key = data[chr(k)]

                    if key is not "":
                        dest_dir = os.path.join(key, im_name)
                        os.rename(im_path, dest_dir)
                        print("[INFO] Moved " + im_name + " to " + dest_dir)
                        print()

                        data = [im_num, image, im_path]
                        images.remove(data)

                        cv2.destroyWindow(name)
                        if im_num == im_max:
                            im_num -= 1
                    else:
                        print("[INFO] No directory shortcut associated with the given key!")


if __name__ == "__main__":
    print("[INFO] Initiating manual image categorization...")
    print()

    clean_directory()
    images = load_imgs()
    sort(images)
