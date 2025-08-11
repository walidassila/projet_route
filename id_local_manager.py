class IDLocalManagerFast:
    def __init__(self):
        self.active_ids = []  # list of tuples (id_local, id_global, id_class, marqueur)

        # Index pour accélérer les recherches :
        self.idx_global = {}  # id_global -> index dans active_ids
        self.idx_class = {}   # id_class -> set des indices dans active_ids

        self._need_rebuild = False  # flag pour reconstruire les index quand nécessaire

    def _rebuild_indices(self):
        self.idx_global.clear()
        self.idx_class.clear()
        for i, (_, id_global, id_class, _) in enumerate(self.active_ids):
            self.idx_global[id_global] = i
            self.idx_class.setdefault(id_class, set()).add(i)
        self._need_rebuild = False

    def update_removed(self, removed_stracks):
            removed_globals = {t.track_id for t in removed_stracks}

            # Calculer le nombre d'objets par classe hors removed
            class_counts = {}
            for _, id_global, id_class, _ in self.active_ids:
                if id_global not in removed_globals:
                    class_counts[id_class] = class_counts.get(id_class, 0) + 1

            to_remove = []
            to_mark = []

            for i, (id_local, id_global, id_class, marked) in enumerate(self.active_ids):
                if id_global in removed_globals:
                    # Si plus aucun autre actif dans la classe → marquer
                    if class_counts.get(id_class, 0) == 0:
                        to_mark.append(i)
                    else:
                        to_remove.append(i)

            # Marquer les objets (sans reconstruire)
            for i in to_mark:
                id_local, id_global, id_class, _ = self.active_ids[i]
                self.active_ids[i] = (id_local, id_global, id_class, True)

            # Supprimer les objets (en partant de la fin pour éviter les décalages)
            for i in sorted(to_remove, reverse=True):
                self.active_ids.pop(i)

            # Reconstruire une seule fois après suppression/marquage
            if to_remove or to_mark:
                self._rebuild_indices()

            # Retourner la liste des éléments supprimés pour info (optionnel)
            return [(id_local, id_global, id_class) for i, (id_local, id_global, id_class, _) in enumerate(self.active_ids) if i in to_remove]


    def get_or_add(self, id_global, id_class):
        if self._need_rebuild:
            self._rebuild_indices()

        # Si déjà existant, retourner l'id_local
        if id_global in self.idx_global:
            idx = self.idx_global[id_global]
            return self.active_ids[idx][0]

        # Chercher un objet marqué dans la même classe
        marked_idx = None
        if id_class in self.idx_class:
            for i in self.idx_class[id_class]:
                if self.active_ids[i][3] is True:
                    marked_idx = i
                    break

        if marked_idx is not None:
            id_local_old, id_global_old, id_class_old, _ = self.active_ids[marked_idx]
            new_local = id_local_old + 1

            # Supprimer ancien marqué et ajouter nouveau
            self.active_ids.pop(marked_idx)
            self.active_ids.append((new_local, id_global, id_class, False))

            # Rebuild indices après modifications
            self._rebuild_indices()

            return new_local

        # Sinon, max id_local + 1 dans cette classe
        max_local = 0
        if id_class in self.idx_class:
            for i in self.idx_class[id_class]:
                max_local = max(max_local, self.active_ids[i][0])

        new_local = max_local + 1
        self.active_ids.append((new_local, id_global, id_class, False))

        # Rebuild indices après ajout
        self._rebuild_indices()

        return new_local
