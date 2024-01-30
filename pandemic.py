import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Pandemic")

# Create a label widget
label = tk.Label(root, text="Hello, Tkinter!")
label.pack()

# Create a button widget
button = tk.Button(root, text="Start Game", command=lambda: label.config(text="Game Started!"))
button.pack()

#MAP CODE
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# Create a plot with a specific projection
fig = plt.figure(figsize=(10, 5))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

# Add coastlines and countries to the map
ax.coastlines()
ax.add_feature(cartopy.feature.BORDERS, linestyle=':')

# Set the extent of the map (optional)
# ax.set_extent([-180, 180, -90, 90])

# Display the map
plt.show()



# Start the application
root.mainloop()