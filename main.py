
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

	image_label: tk.Label
	text_label: tk.Label



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

		self.root_dir = "C:/Users/siche/OneDrive/Documents/git_repos/pokemoneggdisplay/"
		self.gifs_dir = self.root_dir + "egggifs/"
		self.data_dir = self.root_dir + "data/"

		self.progression_chance = 0.5

		self.players = []
		self.num_eggs = 0

		self.window = tk.Tk()

		max_columns = 2
		max_rows = 1
		rectangle_w_to_h = 3 / 2
		self.display_formatter = DisplayFormatter(self.window, max_columns, max_rows, rectangle_w_to_h)

		self.window.configure(background='white')
		self.window.title("EGG INCUBATOR")
		self.window.geometry("%dx%d" % (self.display_formatter.window_width, self.display_formatter.window_height))

		self.gifs = []
		self.gifs.append(Gif(self.gifs_dir + "snorlax.gif", self.display_formatter.get_image_width()))
		self.gifs.append(Gif(self.gifs_dir + "pikachucrop.gif", self.display_formatter.get_image_width()))
		self.gifs.append(Gif(self.gifs_dir + "egghatchcrop.gif", self.display_formatter.get_image_width()))

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
			if player.level < len(self.gifs) - 1:
				if random.random() <= player.promotion_chance:
					print("Player ", player.name, " progressed to stage ", player.level + 1, " after ", player.gamba_attempts, " attempts")
					player.level += 1
					player.promotion_chance = 0.0
					player.gamba_attempts = 0
					self.backup_data()
				if random.random() <= 0.25:
					player.promotion_chance += 0.0001 * player.gamba_attempts
				player.gamba_attempts += 1
		self.window.after(60000, lambda: self.gamba())


	def animate(self):
		for gif in self.gifs:
			gif.change_frame()
		for player in self.players:
			newImage = self.gifs[player.level].get_current_frame()
			player.image_label.config(image = newImage)
			player.image_label.image = newImage
		self.window.after(50, lambda: self.animate())


	def load_data(self):
		file_saves = os.listdir(self.data_dir)
		if len(file_saves) == 0:
			return
		last_save = sorted(file_saves)[-1]
		f = open(self.data_dir + last_save, "r")
		for player_data in f:
			player_data = player_data.split(",")
			self.add_player(player_data[0], player_data[1], int(player_data[2]), int(player_data[3]), float(player_data[4]))


	def regularly_backup_data(self):
		self.backup_data()
		five_minute_timer = 60000 * 5
		self.window.after(five_minute_timer, lambda: self.regularly_backup_data())


	def backup_data(self):
		if len(self.players) > 0:
			new_file_name = self.data_dir + datetime.now().strftime('%y_%m_%d__%H_%M_%S') + "egg_data.csv"
			f = open(new_file_name, "w")
			for player in self.players:
				f.write(player.name + "," + player.time_created + "," + str(player.level) + "," + str(player.gamba_attempts) + "," + str(player.promotion_chance) + "\n")

 
	def add_new_player(self):
		player_name = self.text_box.get()
		if len(player_name) == 0:
			return
		for player in self.players:
			if player.name == player_name:
				return

		player_creation_time = datetime.now().strftime('%H:%M:%S')
		self.add_player(player_name, player_creation_time, 0, 0, 0.0)
		self.text_box.delete(0, 'end')


	def add_player(self, player_name, player_creation_time, player_level, player_gamba_attempts, player_promotion_chance):
		frame = self.gifs[player_level].get_current_frame()
		image_label = tk.Label(self.window, bg="white", image=frame)
		image_label.image = frame
		image_label.grid(row=self.display_formatter.get_image_row(self.num_eggs), column=self.display_formatter.get_image_column(self.num_eggs))

		text_label = tk.Label(self.window, bg="white", text=player_name, font=('Pokemon Classic', 20))
		text_label.grid(row=self.display_formatter.get_text_row(self.num_eggs), column=self.display_formatter.get_text_column(self.num_eggs))

		player = Player(player_name, player_creation_time, player_level, player_gamba_attempts, player_promotion_chance, image_label, text_label)
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

			width = self.display_formatter.get_image_width()
			for gif in self.gifs:
				gif.update_size(width)

		elif self.num_eggs < self.display_formatter.get_min_player_count():
			self.display_formatter.decrease_player_count()

			width = self.display_formatter.get_image_width()
			for gif in self.gifs:
				gif.update_size(width)

		self.refresh_egg_locations()


	def refresh_egg_locations(self):
		i = 0
		for player in self.players:
			player.image_label.grid(row=self.display_formatter.get_image_row(i), column=self.display_formatter.get_image_column(i))
			player.text_label.grid(row=self.display_formatter.get_text_row(i), column=self.display_formatter.get_text_column(i))
			i += 1



if __name__ == '__main__':
	PokemonEggDisplay()
