
from dataclasses import dataclass
from datetime import datetime
import os
import random
import string
import tkextrafont
import tkinter as tk
from PIL import Image, ImageTk

class Gif:
	def __init__(self, file_name, width):
		im = Image.open(file_name)
		self.file_name = file_name
		self.current_frame = 0
		self.num_frames = im.n_frames
		self.update_size(width)

	def change_frame(self):
		self.current_frame += 1
		if self.current_frame >= self.num_frames:
			self.current_frame = 0

	def get_current_frame(self):
		return self.frames[self.current_frame]

	def update_size(self, width):
		im = Image.open(self.file_name)
		zoom = width / im.size[0]
		pixels_x, pixels_y = tuple([int(zoom * x)  for x in im.size])
		self.frames = []
		for i in range(self.num_frames):
			im.seek(i)
			resized_im = im.resize((pixels_x, pixels_y))
			frame = ImageTk.PhotoImage(resized_im)
			self.frames.append(frame)


@dataclass
class Player:
	name: string
	time_created: string
	level: int

	image_label: tk.Label
	text_label: tk.Label


class PokemonEggDisplay:
	def __init__(self):
		self.progression_chance = 0.5
		self.max_columns = 2

		self.players = []
		self.num_eggs = 0

		self.window = tk.Tk()
		self.window_width= self.window.winfo_screenwidth() 
		self.window_height= self.window.winfo_screenheight()

		self.window.configure(background='white')
		self.window.title("EGG INCUBATOR")
		self.window.geometry("%dx%d" % (self.window_width, self.window_height))

		initial_gif_size = self.window_width // self.max_columns - 10
		self.gifs = []
		self.gifs.append(Gif("C:/Users/siche/OneDrive/Documents/pokemoneggdisplay/egggifs/snorlax.gif", initial_gif_size))
		self.gifs.append(Gif("C:/Users/siche/OneDrive/Documents/pokemoneggdisplay/egggifs/pikachucrop.gif", initial_gif_size))
		# self.gifs.append(Gif("C:/Users/siche/OneDrive/Documents/pokemoneggdisplay/egggifs/egghatchcrop.gif"))

		self.data_dir = "C:/Users/siche/OneDrive/Documents/pokemoneggdisplay/data/"

		# Add text entry box
		self.text_box = tk.Entry(self.window, width = 30)
		self.text_box.grid(row=0)

		# Add 'TAKE EGG' button
		self.new_player_button = tk.Button(self.window, text = "TAKE EGG", command = self.add_new_player)
		self.new_player_button.grid(row=1, column=0)

		# Add 'REMOVE EGG' button
		self.remove_player_button = tk.Button(self.window, text = "KILL EGG", command = self.remove_player)
		self.remove_player_button.grid(row=1, column=1)

		# Add 'BACKUP' button
		self.remove_player_button = tk.Button(self.window, text = "BACKUP DATA", command = self.backup_data)
		self.remove_player_button.grid(row=1, column=2)

		self.animate()
		self.regularly_backup_data()
		self.load_data()
		# self.gamba()
		self.window.mainloop()


	# Every minute, players have a 1% chance to progress stages
	def gamba(self):
		for player in self.players:
			if player.level < len(self.gifs) - 1:
				if random.random() <= self.progression_chance:
					player.level += 1
					self.backup_data()
		self.window.after(60000, lambda: self.gamba())

	def animate(self):
		for gif in self.gifs:
			gif.change_frame()
		for player in self.players:
			newImage = self.gifs[player.level].get_current_frame()
			player.image_label.config(image = newImage)
			player.image_label.image = newImage
		self.window.after(50, lambda: self.animate())

	def regularly_backup_data(self):
		self.backup_data()
		five_minute_timer = 60000 * 5
		self.window.after(five_minute_timer, lambda: self.regularly_backup_data())

	def backup_data(self):
		if len(self.players) > 0:
			new_file_name = self.data_dir + datetime.now().strftime('%y_%m_%d__%H_%M_%S') + "egg_data.csv"
			f = open(new_file_name, "w")
			for player in self.players:
				f.write(player.name + "," + player.time_created + "," + str(player.level) + "\n")

	def load_data(self):
		print("Loading data")
		file_saves = os.listdir(self.data_dir)
		last_save = sorted(file_saves)[-1]
		f = open(self.data_dir + last_save, "r")
		for player_data in f:
			player_data = player_data.split(",")
			self.add_player(player_data[0], player_data[1], int(player_data[2]))

	def add_new_player(self):
		player_name = self.text_box.get()
		if len(player_name) == 0:
			return
		for player in self.players:
			if player.name == player_name:
				return

		player_creation_time = datetime.now().strftime('%H:%M:%S')
		self.add_player(player_name, player_creation_time, 0)

	def add_player(self, player_name, player_creation_time, player_level):
		frame = self.gifs[player_level].get_current_frame()
		image_label = tk.Label(self.window, bg="white", image=frame)
		image_label.image = frame
		image_label.grid(row=self.get_image_row(self.num_eggs), column=self.get_image_column(self.num_eggs))

		text_label = tk.Label(self.window, bg="white", text=player_name, font=('Pokemon Classic', 20))
		text_label.grid(row=self.get_text_row(self.num_eggs), column=self.get_text_column(self.num_eggs))

		player = Player(player_name, player_creation_time, player_level, image_label, text_label)
		self.players.append(player)

		self.num_eggs += 1

		# Resize images if full
		if self.num_eggs > self.max_eggs():
			self.max_columns += 1
			width = self.window_width / self.max_columns - 10
			for gif in self.gifs:
				gif.update_size(width)

		self.text_box.delete(0, 'end')

	def remove_player(self):
		player_name = self.text_box.get()
		if len(player_name) == 0:
			return

		for player in self.players:
			if player.name == player_name:

				player.image_label.config(image='')
				player.text_label.config(text="")
				self.text_box.delete(0, 'end')

				self.players.remove(player)
				self.num_eggs -= 1

				self.refresh_egg_locations()
				return

	def refresh_egg_locations(self):
		i = 0
		for player in self.players:
			player.image_label.grid(row=self.get_image_row(i), column=self.get_image_column(i))
			player.text_label.grid(row=self.get_text_row(i), column=self.get_text_column(i))
			i += 1

	def max_eggs(self):
		return self.max_columns * self.max_columns * 2 // 3

	def get_image_row(self, egg_num):
		im_row = 2 + 2 * (egg_num // self.max_columns)
		return im_row

	def get_image_column(self, egg_num):
		im_col = egg_num % self.max_columns
		return im_col

	def get_text_row(self, egg_num):
		text_row = 3 + 2 * (egg_num // self.max_columns)
		return text_row

	def get_text_column(self, egg_num):
		text_col = egg_num % self.max_columns
		return text_col


if __name__ == '__main__':
	print("ilovepokemon")
	PokemonEggDisplay()
