#!/usr/bin/env python

from canBus.CanBus import CanBus
import tkinter as tk


reg_asserv = CanBus.reg_asserv
reg_action = CanBus.reg_action

limite = CanBus.limite

class Console:
    
    
    def __init__(self, root):
        self.bus = CanBus.CanBus("asserv")
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
    
        
    def convert_type(self, x, f: str):
        if f == "d":
            return float(x)
        elif f == "?":
            return bool(float(x))
        elif f == "B":
            return int(x)
        else:
            raise ValueError("Type non spécifé")
        
    def convert(self, reg, msg_name, args):
        formate = reg[msg_name][1]
        if reg[msg_name][0] < 16:
            if len(formate) - len(args) != 2:
                raise ValueError("Nombre d'arguments incorrect")
        else:
            if args:
                raise ValueError("Nombre d'arguments incorrect")
        for i in range(len(args)):
            args[i] = self.convert_type(args[i],formate[i+2])
        
        
    def close(self):
        try:
            self.bus.close()
        except Exception:
            pass
        self.root.quit()
        self.root.destroy()

    def write(self, text):
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        
        

    def process_input(self, event):
        user_input = self.entry.get()

        # Affichage dans la "console"
        self.write(user_input + "\n")
        
        # Quitter la console
        if user_input == "exit":
            self.close()
            return None

        # Envoi de la commande au CAN
        parsed = user_input.split()
        if parsed != []:
            msg_name = parsed[0]
            args = parsed[1:]
            if self.bus.reg == reg_asserv:
                if msg_name in reg_action:
                    self.write("Création d'un nouveau bus\n")
                    try:
                        self.bus.close()
                    finally:
                        self.bus = CanBus.CanBus("action")
                elif msg_name not in reg_asserv:
                    self.write("Veuillez mettre une commande répertoriée\n")
                    self.entry.delete(0, tk.END)
                    self.write(">>> ")
                    return None 
                try:
                    self.convert(self.bus.reg, msg_name, args)
                    if self.bus.reg[msg_name][0] < limite:
                        try:
                            self.bus.send(msg_name, *args)
                        except:
                            self.write("Ereur lors de l'envoi de send()\n")
                    else:
                        try:
                            callback = str(self.bus.request(msg_name))
                            self.write("depuis le LL : " + callback )
                        except:
                            self.write("Erreur lors de l'envoi de request()\n")
                except:
                    self.write("Arguments incorrects\n")
            else:
                if msg_name in reg_asserv:
                    self.write("Création d'un nouveau bus \n")
                    try:
                        self.bus.close()
                    finally:
                        self.bus = CanBus.CanBus("asserv")
                elif msg_name not in reg_action:
                    self.write("Veuillez mettre une commande répertoriée\n")
                    self.entry.delete(0, tk.END)
                    self.write(">>> ")
                    return None 
    
                try:
                    self.convert(self.bus.reg, msg_name, args)
                    if self.bus.reg[msg_name][0] < limite:
                        try:
                            self.bus.send(msg_name, *args)
                        except:
                            self.write("Ereur lors de l'envoi de send()\n")
                    else:
                        try:
                            callback = str(self.bus.request(msg_name))
                            self.write("depuis le LL : " + callback )
                        except:
                            self.write("Erreur lors de l'envoi de request()\n")
                except:
                    self.write("Arguments incorrects\n")
                
        
        # Reset input + nouveau prompt
        self.entry.delete(0, tk.END)
        self.write(">>> ")
        return None 

# Lancement
root = tk.Tk()
Console(root)
root.mainloop()
