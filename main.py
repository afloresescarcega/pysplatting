import os
import struct

from PIL import Image
import time
import argparse

start_time = time.time()

OUTPUT_DIR = "/tmp/splatting/"

PLAY_CANVAS_PLY_HEADER: str = """ply
format binary_little_endian 1.0
element vertex {}
property float x
property float y
property float z
property float f_dc_0
property float f_dc_1
property float f_dc_2
property float opacity
property float rot_0
property float rot_1
property float rot_2
property float rot_3
property float scale_0
property float scale_1
property float scale_2
end_header
"""

OUTPUT_PLY_NAME = "scene_play_canvas_format.ply"

DEBUGGING_TRI_COLOR_VERTICES = [
    {
        'packed_position': [0.0, 1.0, 0.0],
        'packed_color': [255, 0, 0],
        'opacity': [255],
        'packed_rotation': [1.0, 1.0, 0.0, 0.0],
        'packed_scale': [1.0, .1, 0.1]
    },
    {
        'packed_position': [2.0, 2.0, 0.0],
        'packed_color': [0, 255, 0],
        'opacity': [255],
        'packed_rotation': [0.9238, 0.3826, 0.0, 0.0],
        'packed_scale': [.1, 1.0, 0.1]
    },
    {
        'packed_position': [3.0, 0.0, 0.0],
        'packed_color': [0, 0, 255],
        'opacity': [255],
        'packed_rotation': [0.70, 0.70, 0.0, 0.0],
        'packed_scale': [.1, .1, 1.0]
    }
]


def encode_splats_play_canvas_format(vertices) -> bytes:
    # Convert vertex data to binary format
    binary_vertex_data = b''.join(
        struct.pack('<f', val) for vertex in vertices for prop in vertex for val in vertex[prop])
    # Combine header, chunk data, and vertex data
    return PLAY_CANVAS_PLY_HEADER.format(len(vertices)).encode('utf-8') + binary_vertex_data


def get_image(image_path):
    return Image.open(image_path).convert('RGB')


def get_depth(depth_image_path):
    return Image.open(depth_image_path)


def main(im):
    image = get_image(im)
    image_width, image_height = image.size
    z_position = 0.0
    image_vertices = []
    for y_index in range(image_height):
        for x_index in range(image_width):
            current_color = image.getpixel((x_index, y_index))
            packed_position = [x_index, y_index, z_position]
            vertex_data = {
                'packed_position': packed_position,
                'packed_color': [c / 256.0 for c in current_color],
                'opacity': [1.0],
                'packed_rotation': [1.0, 1.0, 0.0, 0.0],
                'packed_scale': [0.1, 0.1, 0.1]
            }
            image_vertices.append(vertex_data)
    combined_data: bytes = encode_splats_play_canvas_format(image_vertices)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_PLY_NAME)

    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(output_path, 'wb') as file:
        b = file.write(combined_data)
        print("Here's the file: ", file.name)
        print(f"The size of the new image is {b} bytes.")
        file_size = os.path.getsize(im)
        print(f"The size of the original image is {file_size} bytes.")
        print(f"Bytes new per original byte: {b / file_size} times")
        end_time = time.time()
        print(f"Execution time: {end_time - start_time} seconds")
        print(f"Execution time over 1hz: {(end_time - start_time) / 0.01667} times over")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process an image file.')
    parser.add_argument('image_path', type=str, help='The path to the image file.')
    args = parser.parse_args()
    print(f"Image path: {args.image_path}")

    main(args.image_path)
