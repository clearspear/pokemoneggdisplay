
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

	gamba_attempts: int
	promotion_chance: float

	hatched_pokemon: string

	image_label: tk.Label
	text_label: tk.Label

	gif: Gif



class DisplayFormatter:
	def __init__(self, window, max_columns, max_rows, rectangle_w_to_h):
		self.window_width= window.winfo_screenwidth()
		self.window_height= window.winfo_screenheight()

		self.max_columns = max_columns
		self.max_rows = max_rows

		self.rectangle_w_to_h = rectangle_w_to_h

		self.button_rows = 2
		self.rows_per_person = 2

	def increase_player_count(self):
		self.max_columns += 1
		self.max_rows = self.max_columns // self.rectangle_w_to_h

	def decrease_player_count(self):
		self.max_columns -= 1
		self.max_rows = self.max_columns // self.rectangle_w_to_h

	def get_image_width(self):
		return self.window_width // self.max_columns - 50

	def get_image_row(self, player_index):
		im_row = self.button_rows + self.rows_per_person * (player_index // self.max_columns)
		return im_row

	def get_image_column(self, player_index):
		im_col = player_index % self.max_columns
		return im_col

	def get_text_row(self, player_index):
		text_row = self.button_rows + 1 + self.rows_per_person * (player_index // self.max_columns)
		return text_row

	def get_text_column(self, player_index):
		text_col = player_index % self.max_columns
		return text_col

	def get_max_player_count(self):
		max_player_count = self.max_columns * self.max_rows
		return max_player_count

	def get_min_player_count(self):
		smaller_count_max_rows = (self.max_columns - 1) // self.rectangle_w_to_h
		min_player_count = (self.max_columns - 1) * smaller_count_max_rows + 1
		return min_player_count



class PokemonEggDisplay:
	def __init__(self):

		#self.root_dir = "C:/Users/siche/OneDrive/Documents/git_repos/pokemoneggdisplay/"
		self.root_dir = "C:/Users/Admin/OneDrive/Documents/git_repos/pokemoneggdisplay/"
		self.gifs_dir = self.root_dir + "egggifs/"
		self.hatched_gifs_dir = self.gifs_dir + "hatchedgifs/"
		self.data_dir = self.root_dir + "data/"

		self.players = []
		self.num_eggs = 0

		self.window = tk.Tk()

		max_columns = 2
		max_rows = 1
		rectangle_w_to_h = 2
		self.display_formatter = DisplayFormatter(self.window, max_columns, max_rows, rectangle_w_to_h)

		self.window.configure(background='white')
		self.window.title("EGG INCUBATOR")
		self.window.geometry("%dx%d" % (self.display_formatter.window_width, self.display_formatter.window_height))

		self.gifs = []
		self.gifs.append(Gif(self.gifs_dir + "stage1.gif", self.display_formatter.get_image_width()))
		self.gifs.append(Gif(self.gifs_dir + "stage25.gif", self.display_formatter.get_image_width()))
		self.gifs.append(Gif(self.gifs_dir + "stage3.gif", self.display_formatter.get_image_width()))

		self.hatched_gifs = []
		hatched_gif_files = os.listdir(self.hatched_gifs_dir)
		for hatched_gif_file in hatched_gif_files:
			self.hatched_gifs.append(Gif(self.hatched_gifs_dir + hatched_gif_file, self.display_formatter.get_image_width()))

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
		self.gamba()
		self.window.mainloop()


	# Every minute, players have a chance to progress stages
	def gamba(self):
		for player in self.players:
			if player.level < len(self.gifs):
				if random.random() <= player.promotion_chance:
					self.promote(player)
				if random.random() <= 0.25:
					player.promotion_chance += 0.0002 * player.gamba_attempts
				player.gamba_attempts += 1
		self.window.after(1000, lambda: self.gamba())


	def promote(self, player):
		print("Player ", player.name, " progressed to stage ", player.level + 1, " after ", player.gamba_attempts, " attempts")
		player.level += 1
		player.promotion_chance = 0.0
		player.gamba_attempts = 0

		if player.level == len(self.gifs):
			random_pokemon = random.randint(0, len(self.hatched_gifs) - 1)
			player.hatched_pokemon = self.hatched_gifs[random_pokemon].file_name
			player.gif = self.hatched_gifs[random_pokemon]
		else:
			player.gif = self.gifs[player.level]

		self.backup_data()


	def animate(self):
		for gif in self.gifs:
			gif.change_frame()
		for hatched_gif in self.hatched_gifs:
			hatched_gif.change_frame()
		for player in self.players:
			player.image_label.config(image = player.gif.get_current_frame())
		self.window.after(100, lambda: self.animate())


	def load_data(self):
		file_saves = os.listdir(self.data_dir)
		if len(file_saves) == 0:
			return
		last_save = sorted(file_saves)[-1]
		f = open(self.data_dir + last_save, "r")
		for player_data in f:
			player_data = player_data.split(",")
			player_data[-1] = player_data[-1].strip()
			self.add_player(player_data[0], player_data[1], int(player_data[2]), int(player_data[3]), float(player_data[4]), player_data[5])


	def regularly_backup_data(self):
		self.backup_data()
		five_minute_timer = 1000 * 5
		self.window.after(five_minute_timer, lambda: self.regularly_backup_data())


	def backup_data(self):
		if len(self.players) > 0:
			new_file_name = self.data_dir + datetime.now().strftime('%y_%m_%d__%H_%M_%S') + "egg_data.csv"
			f = open(new_file_name, "w")
			for player in self.players:
				f.write(player.name + "," + player.time_created + "," + str(player.level) + "," + str(player.gamba_attempts) + "," + str(player.promotion_chance) + "," + player.hatched_pokemon + "\n")

 
	def add_new_player(self):
		player_name = self.text_box.get()
		if len(player_name) == 0:
			return
		for player in self.players:
			if player.name == player_name:
				return

		player_creation_time = datetime.now().strftime('%H:%M:%S')
		self.add_player(player_name, player_creation_time, 0, 0, 0.0, "")
		self.text_box.delete(0, 'end')

		self.backup_data()


	def add_player(self, player_name, player_creation_time, player_level, player_gamba_attempts, player_promotion_chance, hatched_pokemon):
		if hatched_pokemon == "":
			gif = self.gifs[player_level]
		else:
			gif = next(hatched_gif for hatched_gif in self.hatched_gifs if hatched_gif.file_name == hatched_pokemon)

		image_label = tk.Label(self.window, bg="white", image=gif.get_current_frame())
		image_label.grid(row=self.display_formatter.get_image_row(self.num_eggs), column=self.display_formatter.get_image_column(self.num_eggs))

		text_label = tk.Label(self.window, bg="white", text=player_name, font=('Pokemon Classic', 16))
		text_label.grid(row=self.display_formatter.get_text_row(self.num_eggs), column=self.display_formatter.get_text_column(self.num_eggs))

		player = Player(player_name, player_creation_time, player_level, player_gamba_attempts, player_promotion_chance, hatched_pokemon, image_label, text_label, gif)
		self.players.append(player)

		self.num_eggs += 1

		self.refresh_egg_display()


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

		self.refresh_egg_display()


	def refresh_egg_display(self):
		if self.num_eggs > self.display_formatter.get_max_player_count():
			self.display_formatter.increase_player_count()
			self.update_gif_sizes()

		elif self.num_eggs < self.display_formatter.get_min_player_count():
			self.display_formatter.decrease_player_count()
			self.update_gif_sizes()

		self.refresh_egg_locations()


	def update_gif_sizes(self):
		width = self.display_formatter.get_image_width()
		for gif in self.gifs:
			gif.update_size(width)
		for hatched_gif in self.hatched_gifs:
			hatched_gif.update_size(width)


	def refresh_egg_locations(self):
		i = 0
		for player in self.players:
			player.image_label.grid(row=self.display_formatter.get_image_row(i), column=self.display_formatter.get_image_column(i))
			player.text_label.grid(row=self.display_formatter.get_text_row(i), column=self.display_formatter.get_text_column(i))
			i += 1



if __name__ == '__main__':
	PokemonEggDisplay()
