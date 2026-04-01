#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from CanBus import CanBus
import tkinter as tk


reg_asserv = {
    "move" : (0, "<Bd"),
    "rotate" : (1, "<Bd"),
    "set_pos" : (2, "<Bdd"),
    "stop" : (3, "<B"),
    "is_idle" : (16, "<B?"),
    "get_pos" : (17, "<Bddd")
}

reg_action = {
    "lift" : (0, "<BBBBB")
    }

limite = 16

class Console:
    def __init__(self, root):
        self.bus = CanBus("asserv")
        self.root = root
        self.root.title("Commander le robot")

        # Zone de texte (affichage)
        self.text_area = tk.Text(
            root,
            bg="black",
            fg="lime",
            insertbackground="white",
            font=("Courier", 14),
            state="normal"
        )
        self.text_area.pack(expand=True, fill="both")

        # Ligne de saisie
        self.entry = tk.Entry(
            root,
            bg="black",
            fg="lime",
            insertbackground="white",
            font=("Courier", 12)
        )
        self.entry.pack(fill="x")
        self.entry.focus()

        # Bind touche entrée
        self.entry.bind("<Return>", self.process_input)

        # Prompt initial
        self.write(">>> ")

    def write(self, text):
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)

    def process_input(self, event):
        user_input = self.entry.get()

        # Affichage dans la "console"
        self.write(user_input + "\n")
        
        # Quitter la console
        if user_input == "exit":
            self.root.quit() 
            self.root.destroy()

        # Envoi de la commande au CAN
        liste = user_input.split()
        if liste == []:
            self.entry.delete(0, tk.END)
            self.write(">>> ")
            return None
        cmd_text = liste[0]
        liste = liste[1:]
        if cmd_text in reg_asserv:
            if self.bus.reg == reg_action:
                self.write("Création d'un nouveau bus \n")
                try: 
                    self.bus.close()
                finally:
                    self.bus = CanBus("asserv")
            if self.bus.reg[cmd_text][0] < limite:
                try:
                    self.bus.send(cmd_text, *liste)
                except:
                    self.write("Arguments incorrectes")
            else:
                try:
                    self.bus.request(cmd_text, *liste)
                except:
                    self.write("Arguments incorrectes")
        elif cmd_text in reg_action:
            if self.bus.reg == reg_asserv:
                self.write("Création d'un nouveau bus \n")
                try: 
                    self.bus.close()
                finally:
                    self.bus = CanBus("action")
            if self.bus.reg[cmd_text][0] < limite:
                try:
                    self.bus.send(cmd_text, *liste)
                except:
                    self.write("Arguments incorrectes")
            else:
                try:
                    self.bus.request(cmd_text, *liste)
                except:
                    self.write("Arguments incorrectes")
        else:
            self.write("Veuillez mettre une commande répertoriée \n")
            
        return None    
        
        # Reset input + nouveau prompt
        self.entry.delete(0, tk.END)
        self.write(">>> ")

# Lancement
root = tk.Tk()
Console(root)
root.mainloop()
