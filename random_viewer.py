# -*- coding: utf-8 -*-
"""
Creation: Mon May 29 18:02:34 2017
@author: Thomas Blondelle

Description: GUI for viewing all pictures randomly in a directory AND its sub-directories 
optimised for minimum distraction.

"""
from PIL import Image
from PIL import ImageTk

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

import random
import os
import pickle
import subprocess

from pyperclip import copy


class Application(tk.Frame):
    """
    GUI for viewing all pictures randomly in a directory AND its sub-directories
    optimised for minimum distraction.
    Features:    
      - fullscreen by default;
      - .jpg, .jpeg, .png accepted;
      - controlled with mouse or/and keyboard;
      - change directory: F3
    """
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        
        # Initialisation of the window.
        self.master = master
        
        self.master.configure(background='black')
        self.master.wm_title("Random viewer")
        
        self.isfullscreen = True
        self.master.attributes('-fullscreen', self.isfullscreen)
        
        self.index = 0 # While browsing the images.
        
        self.pack()
        
        self.label = tk.Label(borderwidth=0, highlightthickness=0)
        
        # Load list of the images.
        try:
            with open("random_viewer_config.pickle", 'rb') as f:
                self.folder, list_images = pickle.load(f)
            random.shuffle(list_images)
            self.list_images = list_images

        except:
            self.folder = os.getcwd()
            self.list_images = self.create_list_images(self.folder)
       
        while len(self.list_images) == 0:
            messagebox.showwarning('Aucune image', "Il n'y a pas d'image au format jpg, jpeg ou png dans le dossier courant. Veuillez choisir un autre dossier.")
            self.change_dir('_')
       
        self.createWidgets()

    def create_list_images(self, folder):
        """ 
        Create the list of all images in folder and its own folders.
        Stores folder name and filenames in a config file.
        """
        # Find every image in the folder.
        list_images = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".png") or file.endswith(".jpeg") or \
                file.endswith(".jpg") or file.endswith(".JPG") or \
                file.endswith(".JPEG") or file.endswith(".PNG"):
                     list_images.append(os.path.join(root, file))

        # Randomize the list.
        random.shuffle(list_images)
        # Store in config file.
        with open("random_viewer_config.pickle", 'wb') as f:
            pickle.dump((folder, list_images), f)
        return list_images


    def createWidgets(self):
        """Display the current image in the window and add bindings."""

        # Open image file.
        self.image = Image.open(self.list_images[0])
        print('Image {}/{}'.format(self.index + 1 , len(self.list_images)))

        # Resize image.
        window_height = root.winfo_screenheight()
        window_width = int(float(self.image.size[0]) * window_height / float(self.image.size[1]))
        image = self.image.resize((window_width, window_height), Image.BICUBIC)

        # Display image.
        photo = ImageTk.PhotoImage(image)
        self.label.configure(image=photo)
        self.label.image = photo # Keep a reference (otherwise: bugs).
        self.label.pack()
        
        # Create a context_menu menu.
        self.aMenu = tk.Menu(self, tearoff=0, 
                             background='white', 
                             foreground='grey7',
                             relief=tk.FLAT)
        
        self.aMenu.add_command(label="Suivant",accelerator='Espace', hidemargin=True, command=lambda :self.command_next('_'))
        self.aMenu.add_command(label="Précédent", accelerator='Alt+Espace',hidemargin=True, command=lambda :self.command_previous('_'))
        self.aMenu.add_separator()
        self.aMenu.add_command(label="Ouvrir l'emplacement", accelerator='F2', command=lambda :self.open_location('_'))
        self.aMenu.add_command(label="Ouvrir un nouveau dossier", accelerator='Ctrl+N', command=lambda :self.change_dir('_'))
        self.aMenu.add_command(label="Copier la référence", accelerator='Ctrl+C', command=lambda :self.copy_pic('_'))
        self.aMenu.add_separator()
        self.aMenu.add_command(label="Plein écran", accelerator='F11', command=lambda :self.fullscreen('_'))
        self.aMenu.add_separator()
        self.aMenu.add_command(label="Informations", accelerator='F1',command=lambda :self.info_message('_'))
        self.aMenu.add_command(label="À propos", command=lambda :self.about_message('_'))
        self.aMenu.add_separator()
        self.aMenu.add_command(label="Quitter", accelerator='Ctrl+W', command=lambda :self.quit_window('_'))
        
        # Add bindings.
        self.master.bind("<Right>", self.command_next)
        self.master.bind("<space>", self.command_next)
        self.master.bind("<Left>", self.command_previous)
        self.master.bind("<Alt-space>", self.command_previous)
        self.master.bind("<MouseWheel>", self.command_mouse)
        self.master.bind("<F11>", self.fullscreen)
        self.master.bind("<Return>", self.quit_window)
        self.master.bind("<Escape>", self.quit_window)
        self.master.bind("<Control-w>", self.quit_window)
        self.master.bind("<Button-2>", self.quit_window)
        self.master.bind("<F1>", self.info_message)
        self.master.bind("<Double-Button-1>", self.info_message)
        self.master.bind("<F2>", self.open_location)
        self.master.bind("<Control-n>", self.change_dir)
        self.master.bind("<Control-c>", self.copy_pic)
        self.master.bind("<Button-3>", self.context_menu)
    
    def open_location(self, event):
        """Callback function which open a windows explorer window
        selecting the current image file"""
        path = self.list_images[self.index].replace("/", "\\")
        subprocess.call(r'explorer /select,"{}"'.format(path))

    def copy_pic(self, event):
        """Copy the reference of the current image in the clipboard."""
        name = (self.folder + self.list_images[self.index].split(self.folder)[1]).replace("/", "\\")
        copy(name)
        print("Référence copiée.")
        

    def context_menu(self, event):
        self.aMenu.post(event.x_root, event.y_root)
    
    def info_message(self, event):
        """Event which creates on message window about help."""
        name = self.list_images[self.index].split(self.folder)[1]

        help_text = """Affiche une image .jpg, .jpeg, ou .png au hasard se trouvant dans le répertoire ou les sous-répertoires sélectionnés.

Répertoire courant :
    "{}"

Nom de l'image actuelle :
    "{}"

Index actuel : 
    Image {} sur {}""".format(self.folder, name, self.index+1, len(self.list_images))
        messagebox.showinfo('Informations', help_text)
        
    def about_message(self, event):
        """Event which creates on message window about about."""
        messagebox.showinfo('À propos', """Crédits : Thomas Blondelle, Version 1.1, mai 2017.""")
    
    def change_dir(self, event):
        """ Change the current directory and modify the config file."""
        # get filename
        dir_opt = {}
        dir_opt['initialdir'] = 'D:\Documents'
        dir_opt['mustexist'] = False
        dir_opt['parent'] = self.master
        dir_opt['title'] = 'Choisissez un nouveau dossier'
    
        filename = filedialog.askdirectory(**dir_opt)
        
        if filename:
            self.folder = filename
            self.list_images = self.create_list_images(self.folder)
            
            if len(self.list_images) == 0:
                messagebox.showwarning('Aucune image', "Il n'y a pas d'image au format jpg, jpeg ou png dans le dossier courant. Veuillez choisir un autre dossier.")             
                self.change_dir('_')
            else:
                self.index = -1            
                self.command_next('_')

    def quit_window(self, event):
        self.master.quit()

    def fullscreen(self, event):
        self.isfullscreen = not self.isfullscreen
        self.master.attributes('-fullscreen', self.isfullscreen)

    def command_mouse(self, event):
        if event.delta < 0: # Mousewheel going downward.
            self.command_next(event)
        else: # Mousewheel going upward.
            self.command_previous(event)

    def command_next(self,event):
        """ Callback function which displays the next image."""
        # Update index if possible.
        if self.index != len(self.list_images)-1:
            self.index += 1
        
        # Open new image.
        self.image = Image.open(self.list_images[self.index])

        # Resize image.
        window_height = root.winfo_screenheight()
        window_width = int(float(self.image.size[0]) * window_height / float(self.image.size[1]))
        image = self.image.resize((window_width, window_height), Image.BICUBIC)

        # Display image.
        photo = ImageTk.PhotoImage(image)
        self.label.image = photo
        self.label.configure(image=photo)
        print('Image {}/{}'.format(self.index + 1 , len(self.list_images)))

    def command_previous(self,event):
        """ Callback function which displays the previous image."""
        # Update index if possible        
        if self.index != 0:
            self.index -= 1
        
        # Open new image.
        self.image = Image.open(self.list_images[self.index])

        # Resize image.
        window_height = root.winfo_screenheight()
        window_width = int(float(self.image.size[0]) * window_height / float(self.image.size[1]))
        image = self.image.resize((window_width, window_height), Image.BICUBIC)

        # Display image.
        photo = ImageTk.PhotoImage(image)
        self.label.image = photo
        self.label.configure(image=photo)
        print('Image {}/{}'.format(self.index + 1 , len(self.list_images)))


root = tk.Tk()
app = Application(master=root)
app.mainloop()
root.destroy()

