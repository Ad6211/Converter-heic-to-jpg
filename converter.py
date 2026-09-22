import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image
import pillow_heif

# Enregistrer le décodeur HEIF auprès de Pillow
pillow_heif.register_heif_opener()

class ConvertisseurApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Convertisseur HEIC vers JPG")
        self.root.geometry("500x400")
        self.root.configure(bg="#f0f0f0")
        
        self.fichiers_a_convertir = []
        self.dossier_destination = tk.StringVar(value=os.path.expanduser("~\\Desktop"))

        # --- Section Dossier de Destination ---
        frame_dest = tk.Frame(root, bg="#f0f0f0")
        frame_dest.pack(fill="x", padx=20, pady=15)
        
        lbl_dest = tk.Label(frame_dest, text="Dossier de sortie :", bg="#f0f0f0", font=("Arial", 10, "bold"))
        lbl_dest.pack(side="left", padx=5)
        
        ent_dest = tk.Entry(frame_dest, textvariable=self.dossier_destination, font=("Arial", 10), width=35)
        ent_dest.pack(side="left", padx=5, fill="x", expand=True)
        
        btn_parcourir = tk.Button(frame_dest, text="Parcourir...", command=self.choisir_dossier)
        btn_parcourir.pack(side="right", padx=5)

        # --- Zone de Glisser-Déposer ---
        self.drop_zone = tk.Label(
            root, 
            text="Glissez-déposez vos fichiers ou dossiers HEIC ici\n(Fichiers acceptés : .heic)", 
            bg="#ffffff", 
            fg="#555555",
            font=("Arial", 11, "italic"),
            bd=2, 
            relief="dashed",
            height=8
        )
        self.drop_zone.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Activer le Drag & Drop sur cette zone
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.deposer_fichiers)

        # --- Bouton Convertir ---
        self.btn_convertir = tk.Button(
            root, 
            text="Convertir en JPG", 
            command=self.convertir_fichiers,
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            state="disabled"
        )
        self.btn_convertir.pack(fill="x", padx=20, pady=15)

    def choisir_dossier(self):
        dossier = filedialog.askdirectory(initialdir=self.dossier_destination.get())
        if dossier:
            self.dossier_destination.set(dossier)

    def deposer_fichiers(self, event):
        # Nettoyer la chaîne reçue par tkinterdnd2 (gestion des espaces et accolades sous Windows)
        data = event.data
        fichiers = []
        
        # Astuce pour parser correctement les chemins Windows avec espaces entourés d'accolades
        if data.startswith('{'):
            fichiers = [f.strip('{}') for f in data.split('} {')]
        else:
            fichiers = data.split()

        self.fichiers_a_convertir = []
        
        for chemin in fichiers:
            chemin = os.path.abspath(chemin.strip('"'))
            # Si c'est un dossier, on prend tous les .heic à l'intérieur
            if os.path.isdir(chemin):
                for f in os.listdir(chemin):
                    if f.lower().endswith('.heic'):
                        self.fichiers_a_convertir.append(os.path.join(chemin, f))
            # Si c'est un fichier isolé .heic
            elif os.path.isfile(chemin) and chemin.lower().endswith('.heic'):
                self.fichiers_a_convertir.append(chemin)

        nb_fichiers = len(self.fichiers_a_convertir)
        if nb_fichiers > 0:
            self.drop_zone.config(
                text=f"Prêt à convertir : {nb_fichiers} fichier(s) détecté(s).\nGlissez-en d'autres pour modifier la liste.",
                bg="#e7f3fe", fg="#0275d8"
            )
            self.btn_convertir.config(state="normal")
        else:
            self.drop_zone.config(text="Aucun fichier .heic valide trouvé.", bg="#ffebee", fg="#c62828")
            self.btn_convertir.config(state="disabled")

    def convertir_fichiers(self):
        dossier_out = self.dossier_destination.get()
        if not os.path.exists(dossier_out):
            messagebox.showerror("Erreur", "Le dossier de destination n'existe pas.")
            return

        succes = 0
        erreurs = 0

        for chemin_image in self.fichiers_a_convertir:
            try:
                # Ouvrir le fichier HEIC grâce à pillow_heif
                img = Image.open(chemin_image)
                
                # Générer le nom de sortie .jpg
                nom_base = os.path.splitext(os.path.basename(chemin_image))[0]
                chemin_sortie = os.path.join(dossier_out, f"{nom_base}.jpg")
                
                # Sauvegarder au format JPEG
                img.save(chemin_sortie, "JPEG", quality=90)
                succes += 1
            except Exception as e:
                print(f"Erreur sur {chemin_image}: {e}")
                erreurs += 1

        # Message de fin
        self.drop_zone.config(text="Glissez-déposez vos fichiers ou dossiers HEIC ici", bg="#ffffff", fg="#555555")
        self.btn_convertir.config(state="disabled")
        self.fichiers_a_convertir = []
        
        messagebox.showinfo(
            "Conversion terminée", 
            f"Opération terminée !\n\n• Réussis : {succes}\n• Échecs : {erreurs}\n\nFichiers sauvegardés dans :\n{dossier_out}"
        )

if __name__ == "__main__":
    # Utiliser TkinterDnD.Tk au lieu de tk.Tk pour activer le Drag & Drop
    root = TkinterDnD.Tk()
    app = ConvertisseurApp(root)
    root.mainloop()
