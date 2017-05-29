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
import tkinter.filedialog
from tkinter import messagebox

import random
import os
import pickle


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
        
        self.cursor = 0 # While browsing the images.
        
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
        print('{}/{}. {}'.format(self.cursor + 1 , len(self.list_images), 
              self.list_images[self.cursor]))

        # Resize image.
        window_height = root.winfo_screenheight()
        window_width = int(float(self.image.size[0]) * window_height / float(self.image.size[1]))
        image = self.image.resize((window_width, window_height), Image.BICUBIC)

        # Display image.
        photo = ImageTk.PhotoImage(image)
        self.label.configure(image=photo)
        self.label.image = photo # Keep a reference (otherwise: bugs).
        self.label.pack()

        # Add bindings.
        self.master.bind("<Right>", self.command_next)
        self.master.bind("<d>", self.command_next)
        self.master.bind("<Left>", self.command_previous)
        self.master.bind("<q>", self.command_previous)
        self.master.bind("<MouseWheel>", self.command_mouse)
        self.master.bind("<Down>", self.fullscreen)
        self.master.bind("<f>", self.fullscreen)
        self.master.bind("<F11>", self.fullscreen)
        self.master.bind("<Return>", self.quit_window)
        self.master.bind("<Escape>", self.quit_window)
        self.master.bind("<Button-2>", self.quit_window)
        self.master.bind("<F1>", self.help_message)
        self.master.bind("<Button-1>", self.help_message)
        self.master.bind("<F2>", self.filename_message)
        self.master.bind("<Button-3>", self.filename_message)
        self.master.bind("<F3>", self.change_dir)
        
    
    def help_message(self, event):
        """Event which creates on message window about help."""
        help_text = """Affiche une image .jpg, .jpeg, ou .png au hasard se trouvant parmi les {} existantes dans le répertoire ou les sous-répertoires de :
   "{}"

Navigation :
   * Précédant : GAUCHE, Q, Scroll haut
   * Suivant : DROIT, D, Scroll bas
   * Plein écran : BAS, F, F11
   * Aide : F1, Clic gauche
   * Nom de l'image actuelle : F2, Clic droit
   * Changer de répertoire : F3
   * Quitter : Entrée, Echap, Molette
   
Crédits : Thomas Blondelle, Version 1.0, mai 2017.""".format(len(self.list_images), self.folder)
        
        messagebox.showinfo('Aide', help_text)
        
    def filename_message(self, event):
        """Event that display the filename of the current image."""
        messagebox.showinfo("Info", "Nom du fichier :\n{}".format(self.list_images[self.cursor]))
        
        
    def change_dir(self, event):
        """ Change the current directory and modify the config file."""
        # get filename
        dir_opt = {}
        dir_opt['initialdir'] = 'D:\Documents'
        dir_opt['mustexist'] = False
        dir_opt['parent'] = self.master
        dir_opt['title'] = 'Choisissez un nouveau dossier'
    
        filename = tkinter.filedialog.askdirectory(**dir_opt)
        
        if filename:
            self.folder = filename
            self.list_images = self.create_list_images(self.folder)
            
            if len(self.list_images) == 0:
                messagebox.showwarning('Aucune image', "Il n'y a pas d'image au format jpg, jpeg ou png dans le dossier courant. Veuillez choisir un autre dossier.")             
                self.change_dir('_')
            else:
                self.cursor = -1            
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
        # Update cursor if possible.
        if self.cursor != len(self.list_images)-1:
            self.cursor += 1
        
        # Open new image.
        self.image = Image.open(self.list_images[self.cursor])

        # Resize image.
        window_height = root.winfo_screenheight()
        window_width = int(float(self.image.size[0]) * window_height / float(self.image.size[1]))
        image = self.image.resize((window_width, window_height), Image.BICUBIC)

        # Display image.
        photo = ImageTk.PhotoImage(image)
        self.label.image = photo
        self.label.configure(image=photo)
        print('{}/{} - {}'.format(self.cursor + 1 , len(self.list_images), 
              self.list_images[self.cursor]))

    def command_previous(self,event):
        """ Callback function which displays the previous image."""
        # Update cursor if possible        
        if self.cursor != 0:
            self.cursor -= 1
        
        # Open new image.
        self.image = Image.open(self.list_images[self.cursor])

        # Resize image.
        window_height = root.winfo_screenheight()
        window_width = int(float(self.image.size[0]) * window_height / float(self.image.size[1]))
        image = self.image.resize((window_width, window_height), Image.BICUBIC)

        # Display image.
        photo = ImageTk.PhotoImage(image)
        self.label.image = photo
        self.label.configure(image=photo)
        print('{}/{} - {}'.format(self.cursor + 1 , len(self.list_images), 
              self.list_images[self.cursor]))


root = tk.Tk()
app = Application(master=root)
app.mainloop()
root.destroy()

