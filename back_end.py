
import yaml
import random
import copy
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import math

OUTBREAK_LIMIT = 8
CUBE_LIMIT = 3
CURE_LIMIT = 5
MAX_PLAYERS = 8
NUMBER_OF_ACTIONS = 4
INFECTION_RATE = [2,2,2,3,3,4,4,0]
NICE_CARD_DECK = ["One Quiet Night", "Baby Baby"]
overlay_image_id = None

#IMAGE
LARGE_ICON_ACTIVE_X = 280
LARGE_ICON_ACTIVE_Y = 535 #555  # Anchor for all large box display items
LARGE_ICON_PASSIVE_Y = 685 #705 # Anchor for all small  box display items
LARGE_ICON_OFFSET = 450
LARGE_ICON_WIDTH = 159
OVAL_WIDTH = 14
OVAL_HEIGHT = 25
OVAL_OFF_BOARD = 1000
MAP_BOTTOM = 830    # Bottom of canvas
MAP_SIDE = 1450    # Right side of canvas


#COLORS
RESET = "\033[0m"  # Reset to default color
BLUE = "\033[34m"  # Blue text
RED = "\033[31m"   # Red text
BLACK = "\033[30m"   # Black text
YELLOW = "\033[33m"  # Yellow text

class GUI:
    def __init__(self):
        print("GUI created")
        self.root = tk.Tk()
        self.root.geometry("%sx%s" % (MAP_SIDE, MAP_BOTTOM))
        self.main_frame = tk.Frame(self.root)
        self.canvas = None
        self.scrollbar = None
        self.oval = None
        self.research_station_image = None
        self.button_dict = {}

        self.number_of_players = 4

        self.game = GAME(self.number_of_players)
        # Create emply gui arrays for user info

        self.player_image_id = [0] * self.number_of_players
        self.tk_overlay_image = [0] * self.number_of_players
        self.tk_overlay_image_large = [0] * self.number_of_players
        self.large_icon_image = [0] * self.number_of_players
        self.text_items_player_name = [0] * self.number_of_players
        self.text_player_alt_info = [0] * self.number_of_players
        self.black_background = []
        self.general_image = []
        self.text_outbreaks = None
        self.text_infection_rate = None

        #State Machine
        self.player_pointer = 0
        self.actions = 0

        self.pandemic_gui()

    def pandemic_gui(self):
        # Initialize the main Tkinter window
        self.root.title("Image with Overlay and Menu Buttons")
        self.root.grid_rowconfigure(0, weight=1)  # Makes row 0 expandable
        self.root.grid_columnconfigure(0, weight=1)  # Makes column 0 expandable


        # Load the image
        image_path = "world_map.jpg"  # Replace with your image path
        image = Image.open(image_path)
        image_width, image_height = image.size

        # Convert the image to a Tkinter-compatible format
        tk_image = ImageTk.PhotoImage(image)

        #Add tokens
        for i in range(self.number_of_players):
            if i < MAX_PLAYERS:
                overlay_image_path = "player%s.png" % str(i)  # Replace with overlay image path
                overlay_image = Image.open(overlay_image_path)
                overlay_image = overlay_image.resize((60, 60))  # Resize to make it smaller
                self.tk_overlay_image_large[i] = ImageTk.PhotoImage(overlay_image)
                overlay_image = overlay_image.resize((25, 25))  # Resize to make it smaller
                self.tk_overlay_image[i] = ImageTk.PhotoImage(overlay_image)


            else:
                print("Too many players!")

        self.main_frame.pack(expand=True, fill="both")

        # Create a Canvas to display the image and overlay buttons
        self.canvas = tk.Canvas(self.main_frame, width=image_width, height=image_height)
        self.canvas.pack(expand=True, fill="both")

        # Add a Scrollbar
        self.scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure Canvas to use Scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

        # Display the image on the Canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
        self.place_black_background(0, 0, MAP_SIDE, MAP_BOTTOM)

        #add rectangle to bottom left
        self.add_rectangle(20, LARGE_ICON_ACTIVE_Y - 5, 350, MAP_BOTTOM)

        # Add outbreak text
        self.add_outbreaks_text(0)

        #Add infection rate text
        self.add_infection_rate_text()

        # Add lines on map
        for key, city in self.game.city_dict.items():
            self.add_line(city)

        # Add cities on map
        for key, city in self.game.city_dict.items():
            self.add_button(city.name, city.x, city.y, city.color)

        #Add Oval
        self.place_oval_backdrop(OVAL_OFF_BOARD,OVAL_OFF_BOARD)

        #Add research station
        rs_image = Image.open("research_station.png")  # Replace with your PNG file
        rs_image = rs_image.resize((20, 20))  # Resize to make it smaller
        self.research_station_image =ImageTk.PhotoImage(rs_image)
        self.place_research_station(self.game.city_dict["Atlanta"].x, self.game.city_dict["Atlanta"].y)

        # Add players on map
        for i in range(len(self.game.player_list)):
            self.place_player(self.game.player_list[i])

            #Add rectangles
            width = 159
            start_point = 350
            if i < len(self.game.player_list) - 1:
                self.add_rectangle(start_point+width*i, LARGE_ICON_PASSIVE_Y-5, start_point+width*(i+1), MAP_BOTTOM)

        self.game_initialize()

        self.root.mainloop()

    def _on_mousewheel(self, event):
        """Scroll the canvas with the mouse wheel."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def add_rectangle(self, x1=50,y1=50,x2=200,y2=150):

        # Draw the rectangle outline
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="white",  # Perimeter color
            width=3,  # Line thickness
            fill=""  # No fill
        )

        # Add black box
        self.place_black_background(x1, y1, x2, y2)

    def add_player_alt_info_text(self):

        # Active player info
        text_x = 50
        text_y = 590
        self.text_player_alt_info[0] = self.canvas.create_text(
            text_x, text_y,
            text="",  # Initial text
            fill="white",
            font=("Arial", 10, "bold"),
            anchor=tk.NW  # Anchor the top-left of the text to (text_x, text_y)
        )

        #self.canvas.itemconfig(self.text_items_player_data[0], text=new_text)

        text_y = 722
        width = 159
        start_point = 355
        for i in range(self.number_of_players - 1):
            self.text_player_alt_info[i+1] = self.canvas.create_text(
                start_point+i*width, text_y,
                text="",  # Initial text
                fill="white",
                font=("Arial", 7, "bold"),
                anchor=tk.NW  # Anchor the top-left of the text to (text_x, text_y)
            )

    def add_warnings_text(self):

        # Active player info
        text_x = 50
        text_y = LARGE_ICON_ACTIVE_Y + 35
        self.text_player_alt_info[0] = self.canvas.create_text(
            text_x, text_y,
            text="",  # Initial text
            fill="white",
            font=("Arial", 10, "bold"),
            anchor=tk.NW  # Anchor the top-left of the text to (text_x, text_y)
        )


        text_y = LARGE_ICON_PASSIVE_Y + 17
        width = 159
        start_point = 355
        for i in range(self.number_of_players - 1):
            self.text_player_alt_info[i+1] = self.canvas.create_text(
                start_point+i*width, text_y,
                text="",  # Initial text
                fill="white",
                font=("Arial", 7, "bold"),
                anchor=tk.NW  # Anchor the top-left of the text to (text_x, text_y)
            )

    def add_outbreaks_text(self, outbreaks=0):
        # add test showing outbreaks
        text_x = 65
        text_y = 55

        self.add_rectangle(50, 10, 135, 90)

        self.place_general_image(50+20, 10+5, 135-20, 90-35, "outbreak.png")

        self.text_outbreaks = self.canvas.create_text(
            text_x, text_y,
            text="%s / %s" % (outbreaks, OUTBREAK_LIMIT),  # Initial text
            fill="RED",
            font=("Arial", 20, "bold"),
            anchor=tk.NW  # Anchor the top-left of the text to (text_x, text_y)
        )

    def update_outbreaks_text(self, outbreaks=0):
        # update outbreak text
        self.canvas.itemconfig(self.text_outbreaks, text="%s / %s" % (outbreaks, OUTBREAK_LIMIT))

    def add_infection_rate_text(self):
        # add test showing outbreaks
        text_x = 200
        text_y = 50

        self.add_rectangle(text_x-5, 10, text_x+100, 90)

        self.place_general_image(text_x-5+32, 10+5, text_x+100-32, 90-40, "infection_rate.png")

        self.text_infection_rate = self.canvas.create_text(
            text_x, text_y,
            text="Current: %s \nNext: %s" % (self.game.infection_rate, INFECTION_RATE[self.game.outbreaks + 1]),  # Initial text
            fill="Yellow",
            font=("Arial", 12, "bold"),
            anchor=tk.NW  # Anchor the top-left of the text to (text_x, text_y)
        )

    def update_infection_rate_text(self):
        # update outbreak text
        try:
            next_rate = INFECTION_RATE[self.game.outbreaks + 1]
        except:
            next_rate = "END"
        self.canvas.itemconfig(self.text_infection_rate, text="Current: %s \nNext: %s" % (self.game.infection_rate, next_rate))


    def add_player_info_text_items(self):

        # Active player info
        text_x = 40
        text_y = LARGE_ICON_ACTIVE_Y
        self.text_items_player_name[0] = self.canvas.create_text(
            text_x, text_y,
            text="",  # Initial text
            fill="white",
            font=("Arial", 23, "bold"),
            anchor=tk.NW  # Anchor the top-left of the text to (text_x, text_y)
        )

        #self.canvas.itemconfig(self.text_items_player_data[0], text=new_text)

        text_y = LARGE_ICON_PASSIVE_Y
        width = 159
        start_point = 355
        for i in range(self.number_of_players - 1):
            self.text_items_player_name[i+1] = self.canvas.create_text(
                start_point+i*width, text_y,
                text="",  # Initial text
                fill="white",
                font=("Arial", 12, "bold"),
                anchor=tk.NW  # Anchor the top-left of the text to (text_x, text_y)
            )

    def add_large_icons(self):
        # Large player icons
        x = LARGE_ICON_ACTIVE_X
        y = LARGE_ICON_ACTIVE_Y

        self.large_icon_image[0] = self.canvas.create_image(
            x,
            y,
            anchor=tk.NW,
            image=self.tk_overlay_image_large[0])

        y = LARGE_ICON_PASSIVE_Y
        width = LARGE_ICON_OFFSET
        start_point = LARGE_ICON_WIDTH
        for i in range(self.number_of_players - 1):
            self.large_icon_image[i+1] = self.canvas.create_image(
            start_point+width*i,
            y,
            anchor=tk.NW,
            image=self.tk_overlay_image_large[i+1])

    def add_button(self, name, x, y, color):
        # self.button_dict[name] = tk.Button(self.root, text=name)
        button = tk.Button(self.root, text=name)
        b = tk.Button(self.root, text=name)
        circle = self.canvas.create_oval(x, y, x + 20, y + 20, fill=color, outline=color)


        text_color = "white"
        if self.game.city_dict[name].color == "yellow":
            text_color = "black"

        text_id = self.canvas.create_text(x + 10, y + 10, text="0", fill=text_color, font=("Helvetica", 10, "bold"))

        label_id = self.canvas.create_text(x + 10, y - 10, text=name, fill="white", font=("Helvetica", 10, "bold"))

        # overlay_button1_window = self.canvas.create_window(x, y, anchor=tk.NW, window=self.button_dict[name])
        # self.button_dict[name] = x
        # Bind click event to the button
        def on_circle_click(event):
            self.do_something(name)

        self.canvas.tag_bind(circle, "<Button-1>", on_circle_click)
        self.canvas.tag_bind(text_id, "<Button-1>", on_circle_click)

        self.button_dict[name] = [circle, text_id, label_id]   #add array with circle, text and label ids

    def add_button_research_station(self):
        button = tk.Button(self.root, text="RS")
        x = 30
        y = MAP_BOTTOM - 45
        circle = self.canvas.create_oval(x, y, x + 40, y + 40, fill="Grey", outline="Black")

        text_color = "white"

        text_id = self.canvas.create_text(x + 20, y + 20, text="R S", fill=text_color, font=("Helvetica", 10, "bold"))

        def on_circle_click(event):
            self.do_something("Research Station")

        self.canvas.tag_bind(circle, "<Button-1>", on_circle_click)
        self.canvas.tag_bind(text_id, "<Button-1>", on_circle_click)

    def add_button_treat(self):
        button = tk.Button(self.root, text="Treat")
        x = 100
        y = MAP_BOTTOM - 45
        circle = self.canvas.create_oval(x, y, x + 40, y + 40, fill="Grey", outline="Black")

        text_color = "white"

        text_id = self.canvas.create_text(x + 20, y + 20, text="Treat", fill=text_color, font=("Helvetica", 10, "bold"))

        def on_circle_click(event):
            self.do_something("Treat")

        self.canvas.tag_bind(circle, "<Button-1>", on_circle_click)
        self.canvas.tag_bind(text_id, "<Button-1>", on_circle_click)

    def add_button_share(self):
        button = tk.Button(self.root, text="Share")
        x = 170
        y = MAP_BOTTOM - 45
        circle = self.canvas.create_oval(x, y, x + 40, y + 40, fill="Grey", outline="Black")

        text_color = "white"

        text_id = self.canvas.create_text(x + 20, y + 20, text="Share", fill=text_color, font=("Helvetica", 10, "bold"))

        def on_circle_click(event):
            self.do_something("Share")

        self.canvas.tag_bind(circle, "<Button-1>", on_circle_click)
        self.canvas.tag_bind(text_id, "<Button-1>", on_circle_click)

    def add_button_cure(self):
        button = tk.Button(self.root, text="Cure")
        x = 240
        y = MAP_BOTTOM - 45
        circle = self.canvas.create_oval(x, y, x + 40, y + 40, fill="Grey", outline="Black")

        text_color = "white"

        text_id = self.canvas.create_text(x + 20, y + 20, text="Cure", fill=text_color, font=("Helvetica", 10, "bold"))

        def on_circle_click(event):
            self.do_something("Cure")

        self.canvas.tag_bind(circle, "<Button-1>", on_circle_click)
        self.canvas.tag_bind(text_id, "<Button-1>", on_circle_click)

    def add_line(self, city):
        x1 = city.x + 10
        y1 = city.y + 10

        line_length_limit = 300

        for connection in city.connections:

            x2 = self.game.city_dict[connection].x + 10
            y2 = self.game.city_dict[connection].y + 10

            if abs(x2 - x1) > line_length_limit:

                if x2 > x1:
                    x2 = 55
                    y2 = (y2+y1)/2

                elif x2 < x1:
                    x2 = 1423
                    y2 = (y2 + y1) / 2


            self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
            self.canvas.create_line(x1, y1, x2, y2, fill="light grey", width=1)

    def place_player(self, player):
        # Place the overlay image on the canvas and store its ID

        x_offset, y_offset = self.get_player_offset(player)

        x = player.city.x
        y = player.city.y
        id = self.canvas.create_image(x + x_offset, y + y_offset, anchor=tk.NW, image=self.tk_overlay_image[player.id])
        self.player_image_id[player.id] = id

    def move_player(self, name, player):

        if self.game.player_move_normal(name, player.id+1) or self.game.player_move_flight(name, player.id+1):
            x_offset, y_offset = self.get_player_offset(player)
            x = self.game.city_dict[name].x + x_offset
            y = self.game.city_dict[name].y + y_offset
            self.move_oval_backdrop(x, y)
            self.canvas.coords(self.player_image_id[player.id], x, y)
            return True

        return False

    def place_oval_backdrop(self, x=400, y=400):

        oval_width = OVAL_WIDTH
        oval_height = OVAL_HEIGHT
        oval_x1 = x
        oval_y1 = y
        oval_x2 = oval_x1 + oval_width
        oval_y2 = oval_y1 + oval_height

        transparent_color = "#FFFFFF"
        self.oval = self.canvas.create_oval(
            oval_x1, oval_y1, oval_x2, oval_y2,
            fill=transparent_color,
            outline="white",  # Optional: outline color
            width=2  # Optional: outline width
        )
        self.canvas.itemconfig(self.oval, stipple="gray25")

    def place_research_station(self, x=10, y=10):
        # This function places reserach stations at position x and y
        print("placing research station")
        # X and Y offsets
        x_offset = 20
        y_offset = 0
        id = self.canvas.create_image(x + x_offset, y + y_offset, anchor=tk.NW, image=self.research_station_image) # return id not used

    def place_black_background(self, x1, y1, x2, y2):
        # Adds black background with opacity at x and y
        b_back_image = Image.open("black_square_opacity.png")  # Replace with your PNG file

        # Large Active Player Box
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        b_back_image = b_back_image.resize((width, height))  # Resize to make it smaller
        self.black_background.append(ImageTk.PhotoImage(b_back_image))

        id = self.canvas.create_image(x1, y1, anchor=tk.NW, image=self.black_background[-1]) # Places black box at last place in the list

    def place_general_image(self, x1, y1, x2, y2, image_name):
        # Adds black background with opacity at x and y
        image = Image.open(image_name)  # Replace with your PNG file

        # Large Active Player Box
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        image = image.resize((width, height))  # Resize to make it smaller
        self.general_image.append(ImageTk.PhotoImage(image))

        id = self.canvas.create_image(x1, y1, anchor=tk.NW, image=self.general_image[-1]) # Places black box at last place in the list



    def move_oval_backdrop(self, x, y):
        oval_x1 = x + 5
        oval_y1 = y
        oval_x2 = oval_x1 + OVAL_WIDTH
        oval_y2 = oval_y1 + OVAL_HEIGHT

        # Update the oval's coordinates
        self.canvas.coords(self.oval, oval_x1, oval_y1, oval_x2, oval_y2)

    def get_player_offset(self, player):
        theta = 2 * 3.14 / self.number_of_players * player.id
        mag = 16
        x_offset = mag * math.cos(theta) + 2.5
        y_offset = mag * math.sin(theta) + 2.5

        return x_offset, y_offset

    def do_something(self, name):
        # self.move_player(name, self.game.player_list[0])
        self.game_resume(name)

    def game_resume(self, name):
        # MAIN LOOP
        self.print_info()

        # 1 - PLAYER ACTIONS
        if name == "Research Station":
            if self.game.player_build_research_station(self.player_pointer+1):
                self.actions += 1
                self.place_research_station(self.game.player_list[self.player_pointer].city.x, self.game.player_list[self.player_pointer].city.y)    #add reserach station image

        elif name == "Treat":
            if self.game.player_treat_disease(self.player_pointer+1):
                self.actions += 1

        elif name == "Share":
            if self.game.player_share_knowledge(self.player_pointer+1):
                self.actions += 1

        elif name == "Cure":
            if self.game.player_discover_cure(self.player_pointer+1):
                self.actions += 1

        elif self.move_player(name, self.game.player_list[self.player_pointer]):
            self.actions += 1

        # 2 - Draw 2 player cards
        # self.canvas.itemconfig(self.button_dict[name][1], text="1")

        # 3 - Infect Cities
        # Update graphics for player change
        self.update_active_player_view()

        # If out of actions
        if self.actions >= NUMBER_OF_ACTIONS:
            self.actions = 0

            self.game.player_draw_player_cards(self.player_pointer+1)

            #Infect cities
            infected_cities = self.game.board_infect_cities() #Board's turn

            # Loop back to player 0 once all players have played
            self.player_pointer += 1
            if self.player_pointer >= self.number_of_players:
                self.player_pointer = 0

            # Update graphics for player change
            self.update_active_player_view()

    def game_initialize(self):

        # Infect cities
        for key, value in self.game.city_dict.items():
            self.canvas.itemconfig(self.button_dict[key][1], text=str(value.disease_cubes))

        # Add player info
        self.add_player_info_text_items()

        #Add large icons
        self.add_large_icons()

        #Add alt player info
        self.add_player_alt_info_text()

        # Build buttons
        self.add_button_research_station()
        self.add_button_treat()
        self.add_button_share()
        self.add_button_cure()

        #UPDATE view
        self.update_active_player_view()

    def update_active_player_view(self):
        # Update background image for active player
        x_offset, y_offset = self.get_player_offset(self.game.player_list[self.player_pointer])
        self.move_oval_backdrop(self.game.player_list[self.player_pointer].city.x + x_offset, self.game.player_list[self.player_pointer].city.y + y_offset)

        #Update Active player data
        self.canvas.itemconfig(self.text_items_player_name[0], text=self.game.player_list[self.player_pointer].user_name)
        self.canvas.coords(self.large_icon_image[self.player_pointer], LARGE_ICON_ACTIVE_X, LARGE_ICON_ACTIVE_Y)

        #String for additional data
        s = ""
        s += "Current City: "
        s += str(self.game.player_list[self.player_pointer].city.name)
        s += "\n"
        s += "Role: "
        s += str(self.game.player_list[self.player_pointer].role)
        s += "\n"
        s += "_______Cards_______\n"
        for i in range(len(self.game.player_list[self.player_pointer].cards)):
            s += str(self.game.player_list[self.player_pointer].cards[i])
            s += "\n"
        self.canvas.itemconfig(self.text_player_alt_info[0], text=s)

        # Update Other player data
        for i in range(self.number_of_players - 1):
            player_index = (self.player_pointer+i+1)%self.number_of_players
            self.canvas.itemconfig(self.text_items_player_name[i+1], text=self.game.player_list[player_index].user_name)
            self.canvas.coords(self.large_icon_image[player_index], LARGE_ICON_OFFSET+(i)*LARGE_ICON_WIDTH, LARGE_ICON_PASSIVE_Y)

            # String for additional data
            s = ""
            s += "Current City: "
            s += str(self.game.player_list[player_index].city.name)
            s += "\n"
            s += "Role: "
            s += str(self.game.player_list[player_index].role)
            s += "\n"
            s += "_______Cards_______\n"
            for j in range(len(self.game.player_list[player_index].cards)):
                s += str(self.game.player_list[player_index].cards[j])
                s += "\n"
            self.canvas.itemconfig(self.text_player_alt_info[i+1], text=s)

        #Update board with infected cities
        for key, value in self.game.city_dict.items():
            self.canvas.itemconfig(self.button_dict[key][1], text=str(value.disease_cubes))

        # Update outbreaks text
        self.update_outbreaks_text(self.game.outbreaks)

        # Update infection rate text
        self.update_infection_rate_text()

    def print_info(self):
        s=''
        s+='**********************\n'
        for i in range(len(self.game.player_list)):
            s+=str(self.game.player_list[i].user_name)
            s+='\n'
            s+=str(self.game.player_list[i].city.name)
            s+='\n'
            s+=str(self.game.player_list[i].cards)
            s+='\n'
            s+=str(self.game.player_list[i].id)
            s+='\n'
        # s+=str(self.game.infection_deck_down)
        # s+='\n'
        # s+=str(self.game.infection_deck_up)
        # s+='\n'

        print(s)

class PLAYER:
    def __init__(self, city, id, user_name='', cards=[], role=None):
        self.city = city
        self.role = None
        self.user_name = user_name
        self.cards = cards
        self.id = id


    def move(self, next_city):

        move_success = False
        for connected_city in self.city.connections:
            if connected_city == next_city.name:
                self.city = next_city
                move_success = True

        if not move_success:
            print("Invalid city!")

        return move_success

class CITY:
    def __init__(self, name, color, population, disease_cubes, research_station, connections, x=1, y=1):
        self.name = name
        self.color = color
        self.population = population
        self.connections = connections
        self.disease_cubes = disease_cubes
        self.research_station = research_station
        self.x = x
        self.y = y


class GAME:
    def __init__(self, number_of_players):

        self.difficulty = 4 #Number of epidemics in deck

        self.outbreaks = 0
        self.infection_rate = INFECTION_RATE[self.outbreaks]
        self.cured_colors = []


        #Initilaize cities
        self.city_dict = {}
        self.fill_city_data()

        #Create Deck
        self.player_card_deck = []

        #Create infection deck
        self.infection_deck_down = []
        self.infection_deck_up = []

        #Initialize board and decks
        self.game_setup()

        # Initialize Players
        self.player_list = []
        for i in range(number_of_players):
            start_city = self.city_dict['Atlanta']
            player_string = "Player %s" % str(i+1)
            temp_player = PLAYER(start_city, i, player_string)
            self.player_list.append(copy.copy(temp_player))

        for i in range(number_of_players):
            self.player_draw_player_cards(i+1, self.get_player_card_start_number(number_of_players))

    def fill_city_data(self):
        with open('city_data.yaml', 'r') as file:
            data = yaml.safe_load(file)

        for city_data in data['cities']:
            temp_city = CITY(city_data['name'], city_data['color'], city_data['population'], city_data['disease_cubes'], city_data['research_station'], city_data['connections'], city_data['location_x'], city_data['location_y'])
            self.city_dict[city_data['name']] = temp_city

    def fill_player_card_deck(self):
        with open('city_data.yaml', 'r') as file:
            data = yaml.safe_load(file)

        # temp_card_deck = []
        for city_data in data['cities']:
            self.player_card_deck.append(city_data['name'])

        random.shuffle(self.player_card_deck)

    def fill_infection_deck(self):
        with open('city_data.yaml', 'r') as file:
            data = yaml.safe_load(file)

        for city_data in data['cities']:
            self.infection_deck_down.append(city_data['name'])

        #Flip top 9 cards
        for i in range(9):
            city = self.infection_deck_down.pop(i)
            self.infection_deck_up.append(city)

        lengthy = round(len(self.infection_deck_down)/self.difficulty,0)
        breakdown_list = []
        for j in range(self.difficulty):
            breakdown_list.append((j+1)*lengthy-1)

        big_temp_deck = []
        print(breakdown_list)
        temp_deck = []
        for i in range(len(self.infection_deck_down)):
            temp_deck.append(self.infection_deck_down[i])

            if i in breakdown_list:
                print(temp_deck)
                temp_deck.append("Epidemic")
                random.shuffle(temp_deck)
                big_temp_deck += temp_deck
                temp_deck = []

        self.infection_deck_down = big_temp_deck

    def get_player_card_start_number(self, num):
        if num == 1:
            return 6
        elif num == 2:
            return 4
        elif num == 3:
            return 3
        elif num == 4:
            return 2
        else:
            return 2


    def lovely_print(self):
        s=''

        color_list = ['blue', 'yellow', 'red', 'black']
        for c in color_list:
            s+='_______________________________________\n'
            s+=c.upper()
            s+='\n'
            s+='_______________________________________\n'


            for key, city in self.city_dict.items():
                if city.color == c:
                    s+=city.name
                    s+='\t'
                    s+='Cubes: '
                    s+=str(city.disease_cubes)
                    s+='\t'
                    s+='Connections: '
                    s+=str(city.connections)
                    s+='\n'

        s+='_______________________________________\n'
        s+='Player INFO:'
        s+='\n'
        s+='_______________________________________\n'
        for player in self.player_list:
            s += player.user_name
            s += '\t'
            s += 'City: '
            s += player.city.name
            s += '\t'
            s += 'Cubes: '
            s += str(player.city.disease_cubes)
            s += '\t'
            s += 'Connections: '
            s += str(player.city.connections)
            s += '\t'
            s += 'Cards: '
            s += str(player.cards)
            s += '\n'

        print(s)

    # --- PLAYER Actions ----
    def player_move_normal(self, city, player=1):
        # Action - Move

        move_success = False
        for connected_city in self.player_list[player-1].city.connections:
            if connected_city == self.city_dict[city].name:
                self.player_list[player-1].city = self.city_dict[city]
                move_success = True

        if not move_success:
            print("Invalid city!")

        return move_success

    def player_move_flight(self, city, player=1):
        # Action - flight

        #Charter flight
        if self.player_list[player-1].city.name in self.player_list[player-1].cards:
            self.player_list[player - 1].cards.remove(self.player_list[player-1].city.name)
            self.player_list[player - 1].city = self.city_dict[city]
            return True

        # Direct flight
        elif city in self.player_list[player-1].cards:
            self.player_list[player - 1].city = self.city_dict[city]
            self.player_list[player - 1].cards.remove(city)
            return True

        #Shuttle Flight
        elif self.player_list[player-1].city.research_station and self.city_dict[city].research_station:
            self.player_list[player - 1].city = self.city_dict[city]
            return True

        print("Flight not valid!")
        return False


    def player_treat_disease(self, player=1):
        #Action - Treat Disease
        if self.player_list[player - 1].city.disease_cubes == 0:
            print("Cannot cure. No Disease cubes")
            return False
        elif self.player_list[player - 1].city.disease_cubes > 0:
            self.player_list[player - 1].city.disease_cubes -= 1
            return True

        return False


    def player_build_research_station(self, player=1):
        # Action - Build research station
        if not self.player_list[player - 1].city.research_station:
            self.player_list[player - 1].city.research_station = True
            return True
        else:
            print("Already Research station")
            return False


    def player_share_knowledge(self, player1=1,player2=1):
        # Action - Share knowledge
        if self.player_list[player1-1].city.name == self.player_list[player2-1].city.name:
            #Move card from player 1 to player 2
            if self.player_list[player1-1].city.name in self.player_list[player1-1].cards:
                self.player_list[player1 - 1].cards.remove(self.player_list[player1-1].city.name)
                self.player_list[player2 - 1].cards.append(self.player_list[player2 - 1].city.name)
                return True

            elif self.player_list[player2 - 1].city.name in self.player_list[player2 - 1].cards:
                self.player_list[player2 - 1].cards.remove(self.player_list[player2-1].city.name)
                self.player_list[player1 - 1].cards.append(self.player_list[player1 - 1].city.name)
                return True

        print("Make sure you're in the same city as the city you're sharing!")
        return False


    def player_discover_cure(self,player=1):
        #Action - Cure disease. Must be at research station and have cure limit amount of cards
        if self.player_list[player-1].city.research_station:
            # Check if 5 of same color
            color_dict = {}
            for city in self.player_list[player-1].cards:
                temp_color = self.city_dict[city].color
                if temp_color not in color_dict:
                    color_dict[temp_color] = 1
                else:
                    color_dict[temp_color] += 1

            for key, value in color_dict.items():
                if value >= CURE_LIMIT:
                    # One of the colors has reached CURE_LIMIT
                    self.cured_colors.append(key)

                    #Clear player's inventory of cards
                    remaining_cards = CURE_LIMIT
                    cards_list = self.player_list[player - 1].cards.copy()
                    for city in cards_list:
                        if self.city_dict[city].color == key and remaining_cards >= 0:
                            self.player_list[player - 1].cards.remove(city)

                        remaining_cards -= 1

                    return True

        print("Not able to cure!")
        return False

    def player_draw_player_cards(self, player, num_of_cards=2):
        removed_cards = []
        value = player - 1

        temp_deck = self.player_list[value].cards.copy()
        for i in range(num_of_cards):
            temp_deck.append(self.player_card_deck[i])
            removed_cards.append(self.player_card_deck[i])

        self.player_list[value].cards = temp_deck

        for card in removed_cards:
            self.player_card_deck.remove(card)

    def board_infect_cities(self):
        # Draw top cards
        city_names_to_return = []

        for i in range(self.infection_rate):
            city_name = self.infection_deck_down.pop(0)

            if city_name != "Epidemic":
                self.infection_deck_up.append(city_name)
                self.infect(city_name)
            elif city_name == "Epidemic":
                print("EPIDEMIC")
                #
                # self.infection_deck_down.append()
            city_names_to_return.append(city_name)

        return city_names_to_return

    def infect(self, city):
        print("INFECTING: " + str(city))
        self.city_dict[city].disease_cubes += 1

        #OUTBREAK!
        if self.city_dict[city].disease_cubes > 3:
            self.city_dict[city].disease_cubes -= 1
            for connected_cities in self.city_dict[city].connections:
                self.infect(connected_cities)

            self.outbreak()


    def outbreak(self):
        self.outbreaks += 1
        print('WARNING! Now at %s Outbreaks out of %s' % (str(self.outbreaks), str(OUTBREAK_LIMIT)))
        self.infection_rate = INFECTION_RATE[self.outbreaks]

    def game_setup(self):

        #Create player deck
        self.fill_player_card_deck()

        #Create infection deck
        self.fill_infection_deck()
        # 9 cards are drawn as starting cities, infect these cities with game start infections
        infection_rate_list = [1,1,1,2,2,2,3,3,3]
        for i in range(len(self.infection_deck_up)):
            self.city_dict[self.infection_deck_up[i]].disease_cubes = infection_rate_list[i]

        #Shuffle deck up and place it back on top
        random.shuffle(self.infection_deck_up)
        for i in range(len(self.infection_deck_up)):
            self.shift_infection_deck_up_to_deck_down()

    def shift_infection_deck_up_to_deck_down(self):
        city = self.infection_deck_up.pop(0)
        self.infection_deck_down.insert(0, city)

    def shift_infection_deck_down_to_deck_up(self):
        city = self.infection_deck_down.pop(0)
        self.infection_deck_up.insert(0, city)


def game_main():
    number_of_players = 8

    game = GAME(number_of_players)




if __name__ == "__main__":
    # game_main()

    # game = GAME(2)
    gui = GUI()