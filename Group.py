class Group:
    def __init__(self, point, color, liberties):
        """
        Create and initialize a new group.
        :param point: the initial stone in the group
        :param color: color of the stones in the group
        :param liberties: liberties of the group
        """
        self.color = color
        self.points = point if isinstance(point, list) else [point]
        self.liberties = liberties

    @property
    def num_liberty(self):
        return len(self.liberties)

    def add_stones(self, pointlist):
        """Add stones to the group."""
        self.points.extend(pointlist)

    def remove_liberty(self, point):
        self.liberties.remove(point)

    def __str__(self):
        """Summarize color, stones, liberties."""
        return f'{self.color} - stones: {self.points}; liberties: {self.liberties}'

    def __repr__(self):
        return str(self)
