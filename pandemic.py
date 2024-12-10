import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

def pandemic_gui():

    # Initialize the main Tkinter window
    root = tk.Tk()
    root.title("Image with Overlay and Menu Buttons")

    # Load the image
    image_path = "world_map.jpg"  # Replace with your image path
    image = Image.open(image_path)
    image_width, image_height = image.size

    # Convert the image to a Tkinter-compatible format
    tk_image = ImageTk.PhotoImage(image)

    # Create a main Frame to hold both the menu and image area
    main_frame = tk.Frame(root)
    main_frame.pack()

    # Create a menu Frame on the left side
    menu_frame = tk.Frame(main_frame, width=100)
    menu_frame.pack(side=tk.LEFT, fill=tk.Y)

    # Add buttons to the menu frame (outside of the image)
    btn1 = tk.Button(menu_frame, text="Button 1")
    btn1.pack(pady=10)
    btn2 = tk.Button(menu_frame, text="Button 2")
    btn2.pack(pady=10)

    # Create a Canvas to display the image and overlay buttons
    canvas = tk.Canvas(main_frame, width=image_width, height=image_height)
    canvas.pack(side=tk.LEFT)

    # Display the image on the Canvas
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)

    # Add buttons directly on top of the image
    overlay_button1 = tk.Button(root, text="Overlay Button 1")
    overlay_button1_window = canvas.create_window(50, 50, anchor=tk.NW, window=overlay_button1)

    overlay_button2 = tk.Button(root, text="Overlay Button 2")
    overlay_button2_window = canvas.create_window(150, 50, anchor=tk.NW, window=overlay_button2)

    # Run the application
    root.mainloop()


if __name__ == "__main__":
    pandemic_gui()