from PIL import Image
import argparse


def message_to_binary(message):
    return "".join(bin(ord(x))[2:].zfill(8) for x in message)


def binary_to_message(message_binary):
    message_binary = message_binary[0:len(message_binary) - len(message_binary) % 8]
    return ''.join([chr(int(x, 2)) for x in [message_binary[i:i + 8] for i in range(0, len(message_binary), 8)]])


def get_end_message_placeholder():
    return " ---ENDMESSAGE---"


def get_end_message_placeholder_binary():
    return message_to_binary(get_end_message_placeholder())


def parse_args():
    parser = argparse.ArgumentParser(description='Hide/recover a message from a PNG bitmap.')
    parser.add_argument('-p', '--path',
                        help='Path to the PNG bitmap in which there is a hidden message.',
                        type=str,
                        required=False
                        )

    message_group = parser.add_mutually_exclusive_group()
    message_group.add_argument('-f', '--file',
                               help='Path the a txt file containing the message the be hidden in the PNG bitmap.',
                               type=str,
                               required=False
                               )
    message_group.add_argument('-m', '--message',
                               help='Message to be hidden into the PNG bitmap.',
                               type=str,
                               required=False
                               )

    parser.add_argument('-o', '--output',
                        help='Location where the output PNG bitmap will be stored.',
                        type=str,
                        required=False
                        )

    args = parser.parse_args()
    return args.path, args.file, args.message, args.output


def load_image(image_path):
    im = Image.open(image_path)
    width, height = im.size
    pixels = im.load()

    return im, width, height, pixels


def modify_pixel(new_r, new_g, new_b, pixel):
    r, g, b, a = pixel

    mod_r = int(bin(r)[:-1] + str(new_r), 2) if new_r is not None else r
    mod_g = int(bin(g)[:-1] + str(new_g), 2) if new_g is not None else g
    mod_b = int(bin(b)[:-1] + str(new_b), 2) if new_b is not None else b

    return mod_r, mod_g, mod_b, a


def hide_message(width, height, pixels, message):
    print("Hiding message [%s...]" % message[0:200])

    message_binary = message_to_binary(message)

    if len(message_binary) > 255 * 3 * width * height:
        raise Exception("Message is too long. Consider using a bigger image (or learn to be more concise!).")

    i = 0
    for y in range(height):
        for x in range(width):
            if i + 3 < len(message_binary):
                new_pixel = modify_pixel(message_binary[i],
                                         message_binary[i + 1],
                                         message_binary[i + 2], pixels[x, y])
                pixels[x, y] = new_pixel

                i = i + 3

    return pixels


def find_message(width, height, pixels):
    message = ""

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            message = message + str(bin(r)[-1])
            message = message + str(bin(g)[-1])
            message = message + str(bin(b)[-1])

            if message.endswith(get_end_message_placeholder_binary()):
                return message[:len(message) - len(get_end_message_placeholder_binary())]

    return message


def main():
    path, file, message, output = parse_args()

    image, width, height, pixels = load_image(path)
    if message is None and file is None and output is None:
        hidden_binary_message = find_message(width, height, pixels)
        print("Hidden message is:")
        print(binary_to_message(hidden_binary_message))
    else:
        if message is None:
            with open(file, "r") as f:
                message = ' '.join([line.replace('\n', '') for line in f.readlines()])
        message = message + get_end_message_placeholder() + "PADDING"
        modified_pixels = hide_message(width, height, pixels, message)
        image.save(output)


if __name__ == '__main__': main()
