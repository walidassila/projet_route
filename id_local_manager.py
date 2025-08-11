class IDLocalManager:
    def __init__(self):
        # Map : clé=(id_global, id_class) -> (id_local, marqueur)
        self.active_map = {}
        # Map : clé=id_class -> {id_global: id_local}
        self.class_map = {}
        # Compteur max par classe
        self.class_counter = {}

    def update_removed(self, removed_stracks):
        """
        Met à jour les IDs actifs en fonction de removed_stracks :
        - Si l'objet est le seul de sa classe -> marquer pour suppression future
        - Sinon -> supprimer immédiatement
        """
        removed_ids = {(t.track_id, int(t.class_id)) for t in removed_stracks}

        for (id_global, id_class) in list(self.active_map.keys()):
            if (id_global, id_class) in removed_ids:
                same_class = self.class_map.get(id_class, {})
                if len(same_class) == 1:
                    # Marquer comme à supprimer
                    id_local, _ = self.active_map[(id_global, id_class)]
                    self.active_map[(id_global, id_class)] = (id_local, True)
                else:
                    # Suppression immédiate
                    self._remove(id_global, id_class)

    def get_or_add(self, id_global, id_class):
        """
        Retourne l'id_local pour un id_global donné, sinon l'ajoute.
        - Si un objet marqué à supprimer existe pour cette classe :
          -> incrémente id_local et supprime l'ancien marqué
        - Sinon, incrémente le compteur de cette classe
        """
        # Déjà présent → retour direct
        if (id_global, id_class) in self.active_map:
            return self.active_map[(id_global, id_class)][0]

        # Chercher si un objet marqué existe
        for (g_id, c_id), (id_local, marqueur) in list(self.active_map.items()):
            if c_id == id_class and marqueur is True:
                new_local = id_local + 1
                self._remove(g_id, c_id)
                self._add(id_global, id_class, new_local)
                return new_local

        # Nouveau complètement → incrémentation
        new_local = self.class_counter.get(id_class, 0) + 1
        self._add(id_global, id_class, new_local)
        return new_local

    def _add(self, id_global, id_class, id_local):
        """Ajoute un ID actif"""
        self.active_map[(id_global, id_class)] = (id_local, False)
        if id_class not in self.class_map:
            self.class_map[id_class] = {}
        self.class_map[id_class][id_global] = id_local
        self.class_counter[id_class] = max(self.class_counter.get(id_class, 0), id_local)

    def _remove(self, id_global, id_class):
        """Supprime un ID actif"""
        self.active_map.pop((id_global, id_class), None)
        if id_class in self.class_map:
            self.class_map[id_class].pop(id_global, None)
            if not self.class_map[id_class]:
                del self.class_map[id_class]
