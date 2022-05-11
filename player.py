from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from mutagen.mp3 import MP3
import customtkinter
import pygame
import tkinter.ttk as ttk
import os
import glob
import shutil
import time

class App(customtkinter.CTk):
	def __init__(self):
		super().__init__()

		self.title("Mp3 Player")
		self.iconbitmap("mp3player/icons/mp3.ico")
		# self.geometry("500x320")
		self.resizable(0, 0)
		self.config(bg = "#181818")

		self.style = ttk.Style()
		self.style.configure("TScale", background = "#181818")

		customtkinter.set_appearance_mode("system")
		customtkinter.set_default_color_theme("green")
		pygame.mixer.init()

		self.paused = False
		self.stopped = False
		self.skipped = False
		self.PATH = os.getenv("LOCALAPPDATA")

		if os.path.exists(f"{self.PATH}/mp3player"):
			pass

		else:
			os.chdir(self.PATH)
			os.mkdir("mp3player")

		# ============ create master frame ============

		self.master_frame = Frame(master = self, bg = "#181818")
		self.master_frame.pack(padx = (0, 40))

		# ============ create songs listbox ============

		self.song_list = Listbox(master = self.master_frame, bg = "black", fg = "green", width = 70, borderwidth = 0, bd = 0, selectbackground = "gray", selectforeground = "black", highlightcolor = "#181818", highlightthickness = 0)
		self.song_list.grid(row = 0, column =  0, pady = 20, padx = (56, 10))
		self.show(True)

		self.song_list.bind("<<ListboxSelect>>", self.play)

		# ============ create buttons images ============

		self.back_ = PhotoImage(file = "mp3player/icons/backward.png")
		self.forward_ = PhotoImage(file = "mp3player/icons/forward.png")
		self.play_ = PhotoImage(file = "mp3player/icons/play.png")
		self.pause_ = PhotoImage(file = "mp3player/icons/pause.png")
		self.stop_ = PhotoImage(file = "mp3player/icons/stop.png")

		# ============ create buttons frame ============

		self.frame = Frame(master = self.master_frame, bg = "#181818")
		self.frame.grid(row = 2)

		# ============ create buttons ============

		self.back_b = Button(master = self.frame, image = self.back_, bd = 0, command = self.backward, bg = "#181818", activebackground = "#181818")
		self.play_b = Button(master = self.frame, image = self.play_, bd = 0, command = self.pause, bg = "#181818", activebackground = "#181818")
		self.stop_b = Button(master = self.frame, image = self.stop_, bd = 0, command = self.stop, bg = "#181818", activebackground = "#181818")
		self.forward_b = Button(master = self.frame, image = self.forward_, bd = 0, command = self.forward, bg = "#181818", activebackground = "#181818")

		self.back_b.grid(row = 2, column = 1)
		self.play_b.grid(row = 2, column = 2)
		self.stop_b.grid(row = 2, column = 3)
		self.forward_b.grid(row = 2, column = 4)

		self.status_bar = customtkinter.CTkLabel(master = self.frame, text = "", fg = "#99a7a7", bg = "#181818")
		self.status_bar.grid(row = 2, column = 0)

		# ============ create status slider ============

		self.song_slider = ttk.Scale(master = self.master_frame, from_ = 0, to = 100, orient = HORIZONTAL, value = 0, command = self.slide, length = 420, style = "TScale")
		self.song_slider.grid(row = 1, column = 0, sticky = W, padx = (56,12))

		# ============ create volume slider ============

		self.volume_slider = customtkinter.CTkSlider(master = self.frame, from_ = 0, to = 1, command = self.volume, width = 100)
		self.volume_slider.set(1)
		self.volume_slider.grid(row = 2, column = 5, sticky = W)

		# ============ create menus ============

		self.menu = Menu(master = self)
		self.config(menu = self.menu)

		# ============ add song menu ============

		self.add_ = Menu(master = self.menu, tearoff = False)
		self.menu.add_cascade(label = "Add Songs", menu = self.add_)
		self.add_.add_command(label = "Add Songs", command = self.add_song)

		# ============ remove song menu ============

		self.remove_ = Menu(master = self.menu, tearoff = False)
		self.menu.add_cascade(label = "Remove Songs", menu = self.remove_)
		self.remove_.add_command(label = "Delete selected song", command = self.del_)
		self.remove_.add_command(label = "Delete all songs", command = self.del_all)

		


	def play_time(self):
		try:
			if self.stopped:
				return

			index = int(self.song_list.curselection()[0])
			value = self.song_list.get(index)
			current_time = pygame.mixer.music.get_pos() / 1000

			time_ = time.strftime("%M:%S", time.gmtime(current_time))
			self.song_length = f"{self.PATH}/mp3player/{value}.mp3"
			self.song_length = MP3(self.song_length)
			self.song_length = self.song_length.info.length

			time_e = time.strftime("%M:%S", time.gmtime(self.song_length))
			current_time += 1

			if int(self.song_slider.get()) == int(self.song_length):
				self.status_bar.config(text = f"{time_e}/{time_e}")

			elif self.paused:
				pass

			elif int(self.song_slider.get()) == int(current_time):
				music_pos = int(self.song_length)
				self.song_slider.config(to = music_pos, value = int(current_time))

			else:
				time_ = time.strftime("%M:%S", time.gmtime(int(self.song_slider.get())))
				self.status_bar.config(text = f"{time_}/{time_e}")

				music_pos = int(self.song_length)
				self.song_slider.config(to = music_pos, value = int(self.song_slider.get()))
				
				next_time = int(self.song_slider.get()) + 1
				self.song_slider.config(value = next_time)

			self.status_bar.after(1000, self.play_time)
		
		except:
			pass

	def slide_update(self):
		time_ = time.strftime("%M:%S", time.gmtime(int(self.song_slider.get())))
		time_e = time.strftime("%M:%S", time.gmtime(self.song_length))
		slider_value = int(self.song_slider.get())
		self.status_bar.config(text = f"{time_}/{time_e}")


	def show(self, deleted):
		if deleted:
			cursor = self.song_list.curselection()

		self.song_list.delete(0, END)


		songs = os.listdir(f"{self.PATH}/mp3player/")
		
		for song in songs:
			self.song_list.insert(END, song.replace(".mp3", ""))

		try:
			self.song_list.activate(cursor[0])
			self.song_list.selection_set(cursor[0], last = None)
		except:
			pass

	def add_song(self):
		song = filedialog.askopenfilenames(title = "Chose a songs", filetypes = (("mp3 Files", "*.mp3"), ))

		if not song:
			return

		else:
			for i in song:
				shutil.copy(i, f"{self.PATH}/mp3player")

			self.show(True)

	def play(self, e):
		self.stopped = False
		self.paused = False

		index = int(self.song_list.curselection()[0])
		value = self.song_list.get(index)
		self.play_b.config(image = self.pause_)

		song = f"{self.PATH}/mp3player/{value}.mp3"
		
		pygame.mixer.music.load(song)
		pygame.mixer.music.play(loops = 0)

		song_length = MP3(song)
		song_length = song_length.info.length

		time_e = time.strftime("%M:%S", time.gmtime(song_length))
		self.status_bar.config(text = f"{00:00}/{time_e}")

		self.song_slider.config(value = 0)
		if not self.skipped:
			self.play_time()
			self.skipped = True


	def pause(self):
		if self.song_list.curselection():
			if self.paused == True:
				self.play_b.config(image = self.pause_)
				pygame.mixer.music.unpause()
				self.paused = False
			else:
				self.play_b.config(image = self.play_)
				pygame.mixer.music.pause()
				self.paused = True
		else:
			pass

	def stop(self):
		self.paused = False
		self.stopped = True
		self.skipped = False
		
		self.song_slider.config(value = 0)
		self.play_b.config(image = self.play_)
		pygame.mixer.music.stop()
		pygame.mixer.music.unload()
		self.song_list.selection_clear(ACTIVE)
		self.status_bar.config(text = "")


	def backward(self):
		try:
			current = self.song_list.curselection()
			if current[0] > 0:
				self.play_b.config(image = self.play_)
				prev_ = current[0] - 1

				self.song_list.selection_clear(0, END)
				self.song_list.activate(prev_)
				self.song_list.selection_set(prev_, last = None)
				self.song_slider.config(value = 0)
				self.play(None)
		except:
			pass


	def forward(self):
		try:
			current = self.song_list.curselection()
			if current[0] < (self.song_list.size() - 1):
				self.play_b.config(image = self.play_)
				next_ = current[0] + 1

				self.song_list.selection_clear(0, END)
				self.song_list.activate(next_)
				self.song_list.selection_set(next_, last = None)
				self.song_slider.config(value = 0)
				self.play(None)
		except:
			pass

	def del_(self):
		try:
			self.paused = False
			self.stopped = True
			self.skipped = False
			
			self.song_slider.config(value = 0)
			index = int(self.song_list.curselection()[0])
			value = self.song_list.get(index)

			pygame.mixer.music.stop()
			pygame.mixer.music.unload()

			path = f"{self.PATH}/mp3player/{value}.mp3"
			os.remove(path)

			self.play_b.config(image = self.play_)
			self.status_bar.config(text = "")
			self.show(False)

		except:
			pass

	def del_all(self):
		warning = messagebox.askyesno("Mp3 Plyaer", "Are you sure to delete all songs?")
		
		if warning:
			paused = False
			stopped = True
			skipped = False

			self.song_slider.config(value = 0)
			pygame.mixer.music.stop()
			pygame.mixer.music.unload()
			
			path = glob.glob(f"{self.PATH}/mp3player/*")
			for i in path:
				os.remove(i)
			
			self.play_b.config(image = self.play_)
			self.status_bar.config(text = "")
			self.show(False)

	def slide(self, e):
		try:
			paused = False
	
			index = int(self.song_list.curselection()[0])
			value = self.song_list.get(index)
			self.play_b.config(image = self.pause_)

			song = f"{self.PATH}/mp3player/{value}.mp3"
			
			pygame.mixer.music.load(song)
			pygame.mixer.music.play(loops = 0, start = int(self.song_slider.get()))
			self.slide_update()
		
		except:
			self.song_slider.config(value = 0)

	def volume(self, e):
		pygame.mixer.music.set_volume(self.volume_slider.get())


	def start(self):
		self.mainloop()

if __name__ == "__main__":
	app = App()
	app.start()