# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "opencv-python>=4.13.0.92",
# ]
# ///

import os

import cv2

file_path = os.path.realpath(__file__)
script_path = os.path.dirname(file_path)


def create_dynamic_templates(image_path, templates_dir):
    """
    Creates templates by letting the user draw a box around the desired area.
    :param image_path: image path
    :param templates_dir: templates directory
    :return:
    """
    img = cv2.imread(image_path)
    if img is None:
        print("Could not load image. Check the path.")
        return

    print("--- INSTRUCTIONS ---")
    print("1. Draw a box around a letter (e.g., the 'N').")
    print("2. Press SPACE or ENTER to confirm the selection.")
    print("3. Look at the console to type the letter name.")
    print("4. Press 'c' to cancel a selection.")
    print("5. Press 'q' to quit.")

    while True:
        # Opens a window to select the Region of Interest (ROI)
        roi = cv2.selectROI(
            "Select Letter (q to quit)", img, showCrosshair=True, fromCenter=False
        )

        # roi returns (x, y, w, h). If width is 0, user cancelled or closed.
        if roi[2] == 0 or roi[3] == 0:
            break

        # Crop the image
        x, y, w, h = int(roi[0]), int(roi[1]), int(roi[2]), int(roi[3])
        crop = img[y : y + h, x : x + w]

        # Ask user for the label
        cv2.destroyWindow("Select Letter (q to quit)")
        label = input("Enter label for this block (e.g. N, A1): ").strip()

        if label:
            file_path = os.path.join(templates_dir, f"{label}.png")
            cv2.imwrite(file_path, crop)
            print(f"Saved {os.path.basename(file_path)}. Draw the next one.")

        print("Select the next one or press 'q' inside the window to quit.")

    cv2.destroyAllWindows()


# Global variables to store mouse position
mouse_x, mouse_y = 0, 0
clicked = False


def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y, clicked

    if event == cv2.EVENT_MOUSEMOVE:
        # Update cursor position
        mouse_x, mouse_y = x, y

    elif event == cv2.EVENT_LBUTTONDOWN:
        # Register the click
        clicked = True


def create_fixed_templates(image_path, templates_dir, box_size=80):
    """
    Creates templates by letting the user move the mouse to position a fixed-size box (e.g., 80x80 pixels).
    :param image_path: image path
    :param templates_dir: templates directory
    :param box_size: box size in pixels
    :return:
    """
    global mouse_x, mouse_y, clicked

    img = cv2.imread(image_path)
    if img is None:
        print("Error: Could not load image.")
        return

    window_name = f"Template Creator (Fixed {box_size}x{box_size})"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)

    print("--- INSTRUCTIONS ---")
    print(f"1. Move mouse to position the {box_size}x{box_size} box.")
    print("2. CLICK to capture the template.")
    print("3. Type the name in the console and press Enter.")
    print("4. Press 'q' to quit.")

    while True:
        # Create a copy of the image to draw the cursor on
        display_img = img.copy()

        # Calculate top-left corner so mouse is in the center
        x1 = max(0, mouse_x - box_size // 2)
        y1 = max(0, mouse_y - box_size // 2)
        x2 = min(img.shape[1], x1 + box_size)
        y2 = min(img.shape[0], y1 + box_size)

        # Adjust x1/y1 if we hit the bottom/right edge
        if x2 == img.shape[1]:
            x1 = x2 - box_size
        if y2 == img.shape[0]:
            y1 = y2 - box_size

        # Draw the green box
        cv2.rectangle(display_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Show the image
        cv2.imshow(window_name, display_img)

        # Handle Click
        if clicked:
            # Crop the actual image (not the one with the green box drawn!)
            crop = img[y1:y2, x1:x2]

            # Show the cropped bit in a separate tiny window for confirmation
            cv2.imshow("Captured Crop", crop)
            # Force UI update
            cv2.waitKey(1)

            # Ask for input
            print(f"\n[Captured at X:{x1}, Y:{y1}]")
            label = input("Enter label for this template (e.g. 'R', 'A1'): ").strip()

            if label:
                file_path = os.path.join(templates_dir, f"{label}.png")
                cv2.imwrite(file_path, crop)
                print(
                    f"Saved {os.path.basename(file_path)}. Move the mouse to capture the next one."
                )
            else:
                print("Cancelled.")

            # Reset
            clicked = False
            cv2.destroyWindow("Captured Crop")

        # Handle Quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    create_fixed_templates(
        image_path=os.path.join(script_path, "tmp", "canvas-stadium.png"),
        templates_dir=os.path.join(script_path, "templates"),
    )
