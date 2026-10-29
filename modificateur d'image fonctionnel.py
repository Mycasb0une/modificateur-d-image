# -*- coding: utf-8 -*-
# Appel de la bibliothèque
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps

# ----- Définition des dimensions de la zone d'affichage -----
AFFICHAGE_LARGEUR = 600
AFFICHAGE_HAUTEUR = 600
# ----- Variables globales -----
image_premiere_version = None  # Stocke la toute première version importée
image_originale = None  # Stocke l'image d'origine
image_modifiee = None   # Stocke l'image après modification
canvas = None           # Zone d'affichage de l'image
btn_ouvrir = None       # Bouton d'ouverture d'image
bouton_ouvrir_dans_canvas = True  # True tant que le bouton est centré dans le canvas

# ----- Variables pour le rognage manuel à la souris -----
mode_rognage_manuel = False   # True quand le mode est activé (la souris dessine un rectangle)
rectangle_rognage = None      # Référence du rectangle pointillé dessiné sur le canvas
debut_x, debut_y = 0, 0       # Coordonnées du clic de départ (en pixels canvas)
taille_image_affichee = (0, 0)   # (largeur, hauteur) de la dernière image affichée dans le canvas
bouton_rognage_manuel = None  # Le bouton "Rognage manuel" lui-même (créé plus bas)

# ----- Palette de couleurs -----
COULEUR_FOND_VOLET = "#2b2d42"      # Bleu-gris foncé pour le panneau gauche
COULEUR_FOND_ZONE = "#edf2f4"       # Gris très clair pour la zone d'image
COULEUR_ACCENT = "#4361ee"          # Bleu accent pour les boutons principaux
COULEUR_ACCENT_HOVER = "#3a56d4"    # Bleu légèrement plus foncé au survol
COULEUR_SECONDAIRE = "#8d99ae"      # Gris-bleu pour les sous-boutons
COULEUR_SECONDAIRE_HOVER = "#717d92"
COULEUR_DANGER = "#ef233c"          # Rouge pour "Réinitialiser"
COULEUR_DANGER_HOVER = "#d61f36"
COULEUR_SUCCES = "#2a9d8f"          # Vert pour "Enregistrer" / "Sauvegarder"
COULEUR_SUCCES_HOVER = "#238b7e"
COULEUR_TEXTE_CLAIR = "#ffffff"
COULEUR_TEXTE_FONCE = "#2b2d42"
POLICE_TITRE = ("Segoe UI", 14, "bold")
POLICE_BOUTON = ("Segoe UI", 10)
POLICE_SOUS_BOUTON = ("Segoe UI", 9)


boutons_miroir_h = []        # Liste des boutons de simétrie horizontale
miroir_h_visible = False     # Indicateur d'affichage de simétrie horizontale

boutons_miroir_v = []        # Liste des boutons de simétrie verticale
miroir_v_visible = False     # Indicateur d'affichage des boutons de simétrie verticale

boutons_negatif = []         # Liste des boutons de l'image en négatif
negatif_visible = False      # Indicateur d'affichage des boutons de l'image en négatif

bouton_rognage = []          # Liste des boutons de rognage
rognage_visible = False      # Indicateur d'affichage des boutons de rognage

boutons_gris = []            # Liste des boutons de conversion en gris
gris_visible = False         # Indicateur d'affichage des boutons de gris


# ----- Fonction utilitaire pour créer un bouton stylé avec effet de survol -----
def creer_bouton_style(parent, text, command, couleur, couleur_hover, width=18,
                        police=POLICE_BOUTON, texte_couleur=COULEUR_TEXTE_CLAIR):
    """ Crée un bouton avec un style plat et un effet de survol """
    btn = Button(
        parent,
        text=text,
        width=width,
        command=command,
        bg=couleur,
        fg=texte_couleur,
        activebackground=couleur_hover,
        activeforeground=texte_couleur,
        font=police,
        relief=FLAT,
        bd=0,
        cursor="hand2",
        highlightthickness=0,
        padx=6,
        pady=6
    )
    # On stocke la couleur "de base" directement SUR le bouton (et pas dans une
    # variable figée au moment de la création). Comme ça, si on change la couleur
    # plus tard (ex: bouton_rognage_manuel qui devient rouge), l'effet de survol
    # utilisera la NOUVELLE couleur au lieu de revenir à l'ancienne.
    btn.couleur_base = couleur
    btn.couleur_survol = couleur_hover
    btn.bind("<Enter>", lambda e: btn.config(bg=btn.couleur_survol))
    btn.bind("<Leave>", lambda e: btn.config(bg=btn.couleur_base))
    return btn


def changer_couleur_bouton(btn, couleur, couleur_hover):
    """ Change durablement la couleur d'un bouton déjà créé (utilisé pour montrer
        qu'un mode est actif, par exemple le rognage manuel en rouge).
        Contrairement à btn.config(bg=...) tout seul, ça met aussi à jour la
        couleur de survol, donc l'effet <Enter>/<Leave> ne l'efface plus. """
    btn.couleur_base = couleur
    btn.couleur_survol = couleur_hover
    btn.config(bg=couleur)


# ----- Fonction de redimensionnement -----
def redimensionner_image(image, largeur_max, hauteur_max):
    """ Redimensionne une image pour qu'elle rentre dans une zone de dimensions maximales """
    image_ratio = image.width / image.height
    zone_ratio = largeur_max / hauteur_max
    if image_ratio > zone_ratio:
        # Image plus large que haute → ajuster en fonction de la largeur
        nouvelle_largeur = largeur_max
        nouvelle_hauteur = int(largeur_max / image_ratio)
    else:
        # Image plus haute que large → ajuster en fonction de la hauteur
        nouvelle_hauteur = hauteur_max
        nouvelle_largeur = int(hauteur_max * image_ratio)

    return image.resize((nouvelle_largeur, nouvelle_hauteur), Image.Resampling.LANCZOS)


# ----- Fonction pour ouvrir une image -----
def ouvrir_image():
    global image_originale, image_modifiee, image_premiere_version, canvas, bouton_ouvrir_dans_canvas

    fichier = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
    if fichier:
        image_originale = Image.open(fichier)
        image_modifiee = image_originale.copy()
        image_premiere_version = image_originale.copy()  # On sauvegarde la toute première version

        # Dès qu'une image est chargée, le bouton "Ouvrir une image" quitte le
        # centre du canvas et se place dans le volet gauche, au-dessus de "Réinitialiser"
        if bouton_ouvrir_dans_canvas:
            deplacer_bouton_ouvrir_vers_volet()
            bouton_ouvrir_dans_canvas = False

        afficher_image(image_modifiee)


def deplacer_bouton_ouvrir_vers_volet():
    """ Détruit le bouton centré dans le canvas et recrée le même bouton dans le
        volet gauche, juste au-dessus du bouton 'Réinitialiser' """
    global btn_ouvrir

    if btn_ouvrir:
        btn_ouvrir.destroy()

    btn_ouvrir = creer_bouton_style(volet_gauche, "📂 Ouvrir une image", ouvrir_image,
                                     COULEUR_ACCENT, COULEUR_ACCENT_HOVER, width=18)
    btn_ouvrir.pack(after=bouton7, pady=(20, 5), padx=12)




#---------Définition des fonctions ------------


def afficher_options_miroir_h():
    """ Affiche ou cache les boutons pour la symétrie horizontale """
    global boutons_miroir_h, miroir_h_visible

    if miroir_h_visible:
        for btn in boutons_miroir_h:
            btn.destroy()
        boutons_miroir_h.clear()
        miroir_h_visible = False
    else:
        boutons = [
            ("✅ Appliquer", appliquer_miroir_horizontale, COULEUR_ACCENT, COULEUR_ACCENT_HOVER)
        ]

        previous_btn = bouton3  # Position sous "Symétrie horizontale"
        
        for text, command, couleur, couleur_hover in boutons:
            btn = creer_bouton_style(volet_gauche, text, command, couleur, couleur_hover,
                                      width=16, police=POLICE_SOUS_BOUTON)
            btn.pack(after=previous_btn, pady=3, padx=16)
            boutons_miroir_h.append(btn)
            previous_btn = btn

        miroir_h_visible = True
        
def miroir_horizontale(image):
    """ Effectue un miroir horizontal (symétrie verticale) """
    return image.transpose(Image.FLIP_LEFT_RIGHT)

def appliquer_miroir_horizontale():
    """ Applique le miroir horizontal sur l'image """
    global image_modifiee
    if image_modifiee:
        image_modifiee = miroir_horizontale(image_modifiee)

        # Redimensionner avant d'afficher
        image_modifiee_resized = redimensionner_image(image_modifiee, AFFICHAGE_LARGEUR, AFFICHAGE_HAUTEUR)
        
        afficher_image(image_modifiee_resized)

def sauvegarder_miroir_h():
    global image_modifiee, image_originale
    if image_modifiee:
            image_originale = image_modifiee.copy()

def reinitialiser_miroir_h():
    global image_originale, image_modifiee
    if image_originale:
        image_modifiee = image_originale.copy()
        afficher_image(image_originale)  # On affiche l'originale directement


def afficher_options_miroir_v():
    """ Affiche ou cache les boutons pour la symétrie verticale """
    global boutons_miroir_v, miroir_v_visible

    if miroir_v_visible:
        for btn in boutons_miroir_v:
            btn.destroy()
        boutons_miroir_v.clear()
        miroir_v_visible = False
    else:
        boutons = [
            ("✅ Appliquer", appliquer_miroir_verticale, COULEUR_ACCENT, COULEUR_ACCENT_HOVER)
        ]

        previous_btn = bouton4  # Position sous "Symétrie verticale"
        
        for text, command, couleur, couleur_hover in boutons:
            btn = creer_bouton_style(volet_gauche, text, command, couleur, couleur_hover,
                                      width=16, police=POLICE_SOUS_BOUTON)
            btn.pack(after=previous_btn, pady=3, padx=16)
            boutons_miroir_v.append(btn)
            previous_btn = btn

        miroir_v_visible = True
        
def miroir_verticale(image):
    """ Effectue un miroir vertical (symétrie horizontale) """
    return image.transpose(Image.FLIP_TOP_BOTTOM)

def appliquer_miroir_verticale():
    """ Applique le miroir vertical sur l'image """
    global image_modifiee
    if image_modifiee:
        image_modifiee = miroir_verticale(image_modifiee)

        # Redimensionner avant d'afficher
        image_modifiee_resized = redimensionner_image(image_modifiee, AFFICHAGE_LARGEUR, AFFICHAGE_HAUTEUR)

        afficher_image(image_modifiee_resized)
        
def sauvegarder_miroir_v():
    global image_modifiee, image_originale
    if image_modifiee:
            image_originale = image_modifiee.copy()
    
def reinitialiser_miroir_v():
    global image_originale, image_modifiee
    if image_originale:
        image_modifiee = image_originale.copy()
        afficher_image(image_originale)  # On affiche l'originale directement

    

def afficher_options_negatif():
    """ Affiche ou cache les boutons pour l'inversion des couleurs """
    global boutons_negatif, negatif_visible

    if negatif_visible:
        for btn in boutons_negatif:
            btn.destroy()
        boutons_negatif.clear()
        negatif_visible = False
    else:
        boutons = [
            ("✅ Appliquer", appliquer_negatif, COULEUR_ACCENT, COULEUR_ACCENT_HOVER)
        ]

        previous_btn = bouton5  # Position sous "Image en négatif"
        
        for text, command, couleur, couleur_hover in boutons:
            btn = creer_bouton_style(volet_gauche, text, command, couleur, couleur_hover,
                                      width=16, police=POLICE_SOUS_BOUTON)
            btn.pack(after=previous_btn, pady=3, padx=16)
            boutons_negatif.append(btn)
            previous_btn = btn

        negatif_visible = True
        
def negatif(image):
    """ Inverse les couleurs de l'image """
    return ImageOps.invert(image.convert('RGB'))

def appliquer_negatif():
    """ Applique l'inversion des couleurs sur l'image """
    global image_modifiee
    if image_modifiee:
        image_modifiee = negatif(image_modifiee)

        # Redimensionner avant d'afficher
        image_modifiee_resized = redimensionner_image(image_modifiee, AFFICHAGE_LARGEUR, AFFICHAGE_HAUTEUR)

        afficher_image(image_modifiee_resized)

def sauvegarder_negatif():
    global image_modifiee, image_originale
    if image_modifiee:
            image_originale = image_modifiee.copy()

def reinitialiser_negatif():
    global image_originale, image_modifiee
    if image_originale:
        image_modifiee = image_originale.copy()
        afficher_image(image_originale)  # On affiche l'originale directement


def afficher_options_rognage():
    """ Affiche ou cache les options de rognage """
    global bouton_rognage, rognage_visible, bouton_rognage_manuel, mode_rognage_manuel

    if rognage_visible:
        # Si le mode rognage manuel était encore actif quand on referme le menu,
        # on le désactive proprement AVANT de détruire son bouton (sinon les
        # fonctions liées à la souris chercheraient à modifier un bouton qui n'existe plus)
        if mode_rognage_manuel:
            canvas.unbind("<ButtonPress-1>")
            canvas.unbind("<B1-Motion>")
            canvas.unbind("<ButtonRelease-1>")
            mode_rognage_manuel = False

        for btn in bouton_rognage:
            btn.destroy()
        bouton_rognage.clear()
        bouton_rognage_manuel = None
        rognage_visible = False
    else:
        options = [
            ("🔹 Petit", lambda: appliquer_rognage("Petit"), COULEUR_SECONDAIRE, COULEUR_SECONDAIRE_HOVER),
            ("🔸 Moyen", lambda: appliquer_rognage("Moyen"), COULEUR_SECONDAIRE, COULEUR_SECONDAIRE_HOVER),
            ("🔶 Grand", lambda: appliquer_rognage("Grand"), COULEUR_SECONDAIRE, COULEUR_SECONDAIRE_HOVER),
            ("🟧 Large", lambda: appliquer_rognage("Large"), COULEUR_SECONDAIRE, COULEUR_SECONDAIRE_HOVER),
            ("🖱️ Rognage manuel", basculer_rognage_manuel, COULEUR_SECONDAIRE, COULEUR_SECONDAIRE_HOVER)
        ]

        previous_btn = bouton1  # Positionner après "Rognage"
        
        for text, command, couleur, couleur_hover in options:
            btn = creer_bouton_style(volet_gauche, text, command, couleur, couleur_hover,
                                      width=16, police=POLICE_SOUS_BOUTON)
            btn.pack(after=previous_btn, pady=3, padx=16)
            bouton_rognage.append(btn)
            previous_btn = btn

            # On garde une référence globale dédiée au bouton "Rognage manuel"
            # car sa couleur change toute seule pour indiquer si le mode est actif
            if text == "🖱️ Rognage manuel":
                bouton_rognage_manuel = btn

        rognage_visible = True

def rogner_image(image, taille_selectionnee):
    """ Applique un rognage sur l'image en fonction de la taille choisie """
    crop_sizes = {
        "Petit": 0.5,
        "Moyen": 0.7,
        "Grand": 0.85,
        "Large": 0.95
    }

    if taille_selectionnee in crop_sizes:
        percent = crop_sizes[taille_selectionnee]
        width, height = image.size
        new_width, new_height = int(width * percent), int(height * percent)
        left = (width - new_width) // 2
        top = (height - new_height) // 2
        right = left + new_width
        bottom = top + new_height
        return image.crop((left, top, right, bottom))
    return image

def appliquer_rognage(taille_selectionnee):
    """ Applique le rognage choisi sur l'image d'origine et met à jour l'affichage """
    global image_originale, image_modifiee

    if image_originale:
        image_modifiee = rogner_image(image_originale, taille_selectionnee)  # Toujours sur l'image originale

        # Redimensionner pour affichage sur le canvas
        image_modifiee_resized = redimensionner_image(image_modifiee, AFFICHAGE_LARGEUR, AFFICHAGE_HAUTEUR)

        afficher_image(image_modifiee_resized)  # Met à jour l'affichage

def sauvegarder_rognage():
    global image_modifiee, image_originale
    if image_modifiee:
            image_originale = image_modifiee.copy()

def reinitialiser_rognage():
    global image_originale, image_modifiee
    if image_originale:
        image_modifiee = image_originale.copy()
        afficher_image(image_originale)  # On affiche l'originale directement


# ===================== ROGNAGE MANUEL À LA SOURIS =====================

def basculer_rognage_manuel():
    """
    Fonction appelée par le bouton '✂️ Rognage manuel'.
    Fait office d'interrupteur : ON si c'était OFF, OFF si c'était ON.
    """
    global mode_rognage_manuel

    # ----- Sécurité : impossible de rogner s'il n'y a pas d'image -----
    if image_originale is None:
        return

    if mode_rognage_manuel:
        # ---------- Le mode était ACTIF -> on le DÉSACTIVE ----------
        canvas.unbind("<ButtonPress-1>")
        canvas.unbind("<B1-Motion>")
        canvas.unbind("<ButtonRelease-1>")
        changer_couleur_bouton(bouton_rognage_manuel, COULEUR_SECONDAIRE, COULEUR_SECONDAIRE_HOVER)
        mode_rognage_manuel = False
    else:
        # ---------- Le mode était INACTIF -> on l'ACTIVE ----------
        canvas.bind("<ButtonPress-1>", debut_rognage_manuel)
        canvas.bind("<B1-Motion>", glissement_rognage)
        canvas.bind("<ButtonRelease-1>", fin_rognage_manuel)
        changer_couleur_bouton(bouton_rognage_manuel, COULEUR_DANGER, COULEUR_DANGER_HOVER)
        mode_rognage_manuel = True


def debut_rognage_manuel(event):
    """ Appelée au clic gauche : on enregistre le point de départ et on
        dessine un premier rectangle (de taille nulle pour l'instant) """
    global debut_x, debut_y, rectangle_rognage

    debut_x, debut_y = event.x, event.y

    if rectangle_rognage:
        canvas.delete(rectangle_rognage)

    rectangle_rognage = canvas.create_rectangle(
        debut_x, debut_y, debut_x, debut_y,
        outline=COULEUR_ACCENT, width=2, dash=(4, 2)
    )


def glissement_rognage(event):
    """ Appelée à chaque mouvement de souris (bouton enfoncé) : on redessine
        le rectangle entre le point de départ et la position actuelle """
    global rectangle_rognage

    if rectangle_rognage:
        canvas.coords(rectangle_rognage, debut_x, debut_y, event.x, event.y)


def fin_rognage_manuel(event):
    """ Appelée au relâchement du clic : on calcule le rectangle final,
        on convertit les coordonnées canvas -> coordonnées image réelle,
        puis on applique le rognage """
    global image_originale, image_modifiee, rectangle_rognage, mode_rognage_manuel

    # Coordonnées du rectangle en pixels canvas (on remet dans l'ordre
    # au cas où l'utilisateur aurait glissé de droite à gauche ou de bas en haut)
    x0, y0 = min(debut_x, event.x), min(debut_y, event.y)
    x1, y1 = max(debut_x, event.x), max(debut_y, event.y)

    # Taille de l'image telle qu'affichée dans le canvas (mémorisée dans afficher_image)
    largeur_affichee, hauteur_affichee = taille_image_affichee

    # L'image est centrée dans le canvas 600x600 : il peut donc y avoir des
    # bandes vides de chaque côté. On calcule ce décalage pour ne pas fausser
    # le calcul si l'image n'est pas parfaitement carrée.
    decalage_x = (AFFICHAGE_LARGEUR - largeur_affichee) // 2
    decalage_y = (AFFICHAGE_HAUTEUR - hauteur_affichee) // 2

    # Facteur d'échelle entre l'image affichée (petite) et l'image réelle (grande)
    echelle_x = image_originale.width / largeur_affichee
    echelle_y = image_originale.height / hauteur_affichee

    # Conversion des coordonnées canvas -> coordonnées de l'image réelle
    gauche = int((x0 - decalage_x) * echelle_x)
    haut = int((y0 - decalage_y) * echelle_y)
    droite = int((x1 - decalage_x) * echelle_x)
    bas = int((y1 - decalage_y) * echelle_y)

    # Sécurité : on borne les valeurs pour rester dans les limites de l'image
    # (si l'utilisateur a cliqué-glissé un peu en dehors de l'image affichée)
    gauche = max(0, min(gauche, image_originale.width))
    droite = max(0, min(droite, image_originale.width))
    haut = max(0, min(haut, image_originale.height))
    bas = max(0, min(bas, image_originale.height))

    # On ne rogne que si le rectangle a une taille minimale
    # (évite un rognage accidentel sur un simple clic sans glissement)
    if droite - gauche > 5 and bas - haut > 5:
        image_modifiee = image_originale.crop((gauche, haut, droite, bas))
        afficher_image(image_modifiee)

    # On efface le rectangle pointillé et on désactive le mode automatiquement,
    # pour que l'utilisateur n'ait pas à recliquer sur le bouton
    if rectangle_rognage:
        canvas.delete(rectangle_rognage)
        rectangle_rognage = None

    canvas.unbind("<ButtonPress-1>")
    canvas.unbind("<B1-Motion>")
    canvas.unbind("<ButtonRelease-1>")
    changer_couleur_bouton(bouton_rognage_manuel, COULEUR_SECONDAIRE, COULEUR_SECONDAIRE_HOVER)
    mode_rognage_manuel = False

# ================== FIN DU ROGNAGE MANUEL À LA SOURIS ==================



def afficher_options_gris():
    """ Affiche ou cache les boutons 'Convertir', 'Réinitialiser' et 'Enregistrer' """
    global boutons_gris, gris_visible

    if gris_visible:
        # Supprimer les boutons s'ils sont visibles
        for btn in boutons_gris:
            btn.destroy()
        boutons_gris.clear()
        gris_visible = False
    else:
        # Ajouter les boutons sous "Convertir en gris"
        boutons = [
            ("✅ Convertir", appliquer_gris, COULEUR_ACCENT, COULEUR_ACCENT_HOVER)
        ]

        previous_btn = bouton2  # Positionner après "Convertir en gris"
        
        for text, command, couleur, couleur_hover in boutons:
            btn = creer_bouton_style(volet_gauche, text, command, couleur, couleur_hover,
                                      width=16, police=POLICE_SOUS_BOUTON)
            btn.pack(after=previous_btn, pady=3, padx=16)
            boutons_gris.append(btn)
            previous_btn = btn

        gris_visible = True

def gris(image):
    """ Convertit l'image en niveaux de gris """
    return image.convert("L")  # Conversion en niveaux de gris

def appliquer_gris():
    """ Convertit l'image en niveaux de gris et met à jour l'affichage """
    global image_originale, image_modifiee

    if image_originale:
        image_modifiee = gris(image_originale)  # Appliquer la conversion en gris

        # Redimensionner pour affichage
        image_modifiee_resized = redimensionner_image(image_modifiee, AFFICHAGE_LARGEUR, AFFICHAGE_HAUTEUR)

        afficher_image(image_modifiee_resized)  # Met à jour l'affichage

def sauvegarder_gris():
    global image_modifiee, image_originale
    if image_modifiee:
            image_originale = image_modifiee.copy()

def reinitialiser_gris():
    global image_originale, image_modifiee
    if image_originale:
        image_modifiee = image_originale.copy()
        afficher_image(image_originale)  # On affiche l'originale directement


    
def reinitialiser_image():
    global image_originale, image_modifiee, image_premiere_version

    if image_premiere_version:
        image_originale = image_premiere_version.copy()  # Remet l'originale en état initial
        image_modifiee = image_premiere_version.copy()
        afficher_image(image_premiere_version)  # Afficher la toute première version
    
def afficher_image(image):
    """ Affiche l'image redimensionnée sur le canvas """
    global canvas, taille_image_affichee

    # Redimensionner uniquement pour l'affichage
    image_redimensionnee = redimensionner_image(image, AFFICHAGE_LARGEUR, AFFICHAGE_HAUTEUR)

    # On mémorise la taille réelle affichée : c'est ce qui permettra plus tard
    # de convertir les coordonnées de la souris (pixels canvas) en coordonnées
    # de l'image d'origine pour le rognage manuel.
    taille_image_affichee = (image_redimensionnee.width, image_redimensionnee.height)

    img_tk = ImageTk.PhotoImage(image_redimensionnee)

    canvas.delete("all")  # Effacer l'image précédente
    canvas.create_image(AFFICHAGE_LARGEUR // 2, AFFICHAGE_HAUTEUR // 2, image=img_tk)
    canvas.image = img_tk  # Sauvegarde la référence

def sauvegarder_image():
    global image_modifiee
    if image_modifiee:
        fichier = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if fichier:
            image_modifiee.save(fichier)



# Création de la fenêtre principale
window = Tk()
window.title("Application de modificateur d'image")
window.configure(background=COULEUR_FOND_ZONE)

# Mise en place d'un label de titre
htLabel = Label(window, text="Modificateur Maison🏡", font=POLICE_TITRE,
                 bg=COULEUR_FOND_ZONE, fg=COULEUR_TEXTE_FONCE, pady=10)
htLabel.pack()

# ----- Gestion des emplacements -----
p = PanedWindow(window, orient=HORIZONTAL, bg=COULEUR_FOND_ZONE, bd=0, sashwidth=4)
p.pack(side=TOP, expand=Y, fill=BOTH, pady=2, padx=2)

# Volet gauche 
volet_gauche = Frame(p, background=COULEUR_FOND_VOLET, width=170, height=400)
p.add(volet_gauche)

# ----- Mise en place des boutons dans le volet gauche -----
bouton1 = creer_bouton_style(volet_gauche, "✂ Rognage", afficher_options_rognage,
                              COULEUR_ACCENT, COULEUR_ACCENT_HOVER, width=18)
bouton1.pack(pady=(16, 5), padx=12)

bouton2 = creer_bouton_style(volet_gauche, "⚫ Convertir en gris", afficher_options_gris,
                              COULEUR_ACCENT, COULEUR_ACCENT_HOVER, width=18)
bouton2.pack(pady=5, padx=12)

bouton3 = creer_bouton_style(volet_gauche, "↔ Symétrie horizontale", afficher_options_miroir_h,
                              COULEUR_ACCENT, COULEUR_ACCENT_HOVER, width=18)
bouton3.pack(pady=5, padx=12)

bouton4 = creer_bouton_style(volet_gauche, "↕ Symétrie verticale", afficher_options_miroir_v,
                              COULEUR_ACCENT, COULEUR_ACCENT_HOVER, width=18)
bouton4.pack(pady=5, padx=12)

bouton5 = creer_bouton_style(volet_gauche, "🌓 Image en négatif", afficher_options_negatif,
                              COULEUR_ACCENT, COULEUR_ACCENT_HOVER, width=18)
bouton5.pack(pady=5, padx=12)

bouton6 = creer_bouton_style(volet_gauche, "💾 Sauvegarder", sauvegarder_image,
                              COULEUR_SUCCES, COULEUR_SUCCES_HOVER, width=18)
bouton6.pack(pady=(20, 5), padx=12)

bouton7 = creer_bouton_style(volet_gauche, "🔄 Réinitialiser", reinitialiser_image,
                              COULEUR_DANGER, COULEUR_DANGER_HOVER, width=18)
bouton7.pack(pady=5, padx=12)

# Volet droit 
volet_droit = Frame(p, background=COULEUR_FOND_ZONE, width=400, height=400)
p.add(volet_droit, stretch="always")

# Zone d'affichage (Canvas) centrée
canvas = Canvas(volet_droit, width=AFFICHAGE_LARGEUR, height=AFFICHAGE_HAUTEUR,
                 bg=COULEUR_FOND_ZONE, highlightthickness=1, highlightbackground=COULEUR_SECONDAIRE)
canvas.pack(expand=True, pady=10)

# ----- Bouton d'ouverture d'image, centré dans le canvas tant qu'aucune image n'est chargée -----

# Illustration de sakura affichée en fond du canvas tant qu'aucune photo n'est ouverte.
# Le fichier doit se trouver dans le même dossier que ce script.
# On la place dans la moitié haute du canvas, et le texte + le bouton en dessous,
# pour que rien ne se superpose à la fleur.
try:
    sakura_originale = Image.open("sakura.png").convert("RGBA")
    sakura_redimensionnee = redimensionner_image(sakura_originale, 260, 260)
    sakura_img_tk = ImageTk.PhotoImage(sakura_redimensionnee)
    canvas.create_image(AFFICHAGE_LARGEUR // 2, 210, image=sakura_img_tk)
except FileNotFoundError:
    print("⚠️ sakura.png introuvable : place l'image dans le même dossier que ce script.")

canvas.create_text(AFFICHAGE_LARGEUR // 2, 400,
                    text="Aucune image chargée", font=POLICE_BOUTON, fill=COULEUR_SECONDAIRE)

btn_ouvrir = creer_bouton_style(canvas, "📂 Ouvrir une image", ouvrir_image,
                                 COULEUR_ACCENT, COULEUR_ACCENT_HOVER, width=22)
canvas.create_window(AFFICHAGE_LARGEUR // 2, 440, window=btn_ouvrir)


# Lancement de la boucle principale
window.mainloop()