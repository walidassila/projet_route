class IDLocalManager:
    def __init__(self):
        # Stocke tous les triplets actifs sous forme:
        # { id_class: [ (id_track_global, id_local), ... ] }
        self.active_ids = {}

    def add(self, id_track_global, id_class):
        """Ajoute un nouveau triplet, crée id_local incrémenté par classe"""
        if id_class not in self.active_ids:
            self.active_ids[id_class] = []

        # Trouver le max id_local existant pour cette classe
        if self.active_ids[id_class]:
            max_local = max(t[1] for t in self.active_ids[id_class])
        else:
            max_local = 0

        new_local = max_local + 1
        self.active_ids[id_class].append((id_track_global, new_local))
        return new_local

    def remove(self, id_track_global, id_class):
        """Supprime un triplet selon la règle donnée"""
        if id_class not in self.active_ids:
            return  # Rien à faire

        # Trouver le triplet à supprimer
        triplets = self.active_ids[id_class]
        triplet_to_remove = None
        for t in triplets:
            if t[0] == id_track_global:
                triplet_to_remove = t
                break
        if triplet_to_remove is None:
            return  # Pas trouvé

        # Vérifier si c'est le dernier id_local (max)
        max_local = max(t[1] for t in triplets)
        if triplet_to_remove[1] == max_local:
            # Ne pas supprimer pour bloquer le compteur local
            # Tu peux ajouter une gestion spéciale ici si besoin
            print(f"Blocage suppression dernier id_local {max_local} pour classe {id_class}")
            return
        else:
            # Supprimer normalement
            triplets.remove(triplet_to_remove)
            if len(triplets) == 0:
                del self.active_ids[id_class]

    def get_local_id(self, id_track_global, id_class):
        """Retourne le id_local correspondant, ou None si pas trouvé"""
        if id_class not in self.active_ids:
            return None
        for t in self.active_ids[id_class]:
            if t[0] == id_track_global:
                return t[1]
        return None
