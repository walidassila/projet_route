import re
import random
import numpy as np
np.float = float 
def generate_model_abbreviations(names_dict):
    """
    Génère un dictionnaire d'abréviations à partir des noms du modèle.

    Args:
        names_dict (dict): dictionnaire {id: nom_classe}

    Returns:
        dict: {id_classe: abréviation}
    """
    abbreviations = {}
    separators = re.compile(r'[ _\.\-/#]+')  # espaces, _, ., -, /, #

    for cls_id, cls_name in names_dict.items():
        # Découper le nom en mots selon les séparateurs
        words = separators.split(cls_name)
        words = [w for w in words if w]  # supprimer les éventuels vides

        if len(words) > 1:
            # Plusieurs mots → première lettre de chaque mot
            abbr = ''.join([w[0].upper() for w in words])
        else:
            # Un seul mot → 3 premiers caractères
            abbr = words[0][:3].upper()

        abbreviations[cls_id] = abbr

    return abbreviations #ex sortie:{0: 'FAI', 1: 'FLP', 2: 'FT', 3: 'NDP', 4: 'ORN', 5: 'PEL', 6: 'PLU', 7: 'RES'}

def replace_name(model,class_names):
    new_names={}
    for i, full_name in model.names.items():
            if full_name in class_names:
                new_names[i] = class_names[full_name]
            else:
                  new_names[i]=full_name
    return new_names #new_names ex({0: "Personne", 1: "Voiture", 2: "dog"})
def replace_color(model, class_colors=None):
    # Couleurs par défaut bien distinctes (20 couleurs)
    default_colors = [
        (255, 0, 0),       # rouge
        (0, 255, 0),       # vert
        (0, 0, 255),       # bleu
        (255, 255, 0),     # jaune
        (255, 0, 255),     # magenta
        (0, 255, 255),     # cyan
        (128, 0, 128),     # violet foncé
        (56, 87, 35),      # vert olive foncé
        (255, 165, 0),     # orange
        (128, 128, 0),     # olive
        (0, 128, 128),     # teal
        (128, 0, 0),       # marron foncé
        (0, 128, 0),       # vert foncé
        (0, 0, 128),       # bleu marine
        (210, 105, 30),    # chocolat
        (139, 69, 19),     # brun
        (255, 20, 147),    # rose profond
        (0, 191, 255),     # bleu ciel
        (47, 79, 79),      # gris foncé
        (255, 215, 0)      # or
    ]
    
    new_colors = {}
    used_colors = set()

    for i, full_name in model.names.items():
        # Si on a une couleur personnalisée pour cette classe, on l'utilise
        if class_colors and full_name in class_colors:
            color = class_colors[full_name]
        else:
            # Si on a encore des couleurs dans default_colors, on prend la suivante
            if default_colors:
                color = default_colors.pop(0)
            else:
                # Sinon, on génère une couleur aléatoire unique
                while True:
                    color = (
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255)
                    )
                    if color not in used_colors:
                        break
        new_colors[i] = color
        used_colors.add(color)

    return new_colors #new_colors ex({  0: (123, 45, 67), 1: (255, 0, 0), 2: (0, 255, 0))} 
   
