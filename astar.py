import heapq


class Node:
    """
    A node class for A* Pathfinding
    """

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __repr__(self):
        return f'{self.position} - g: {self.g} h: {self.h} f: {self.f}'

    # defining less than for purposes of heap queue
    def __lt__(self, other):
        return self.f < other.f

    # defining greater than for purposes of heap queue
    def __gt__(self, other):
        return self.f > other.f


def return_path(current):
    path = []
    while current is not None:
        path.append(current.position)
        current = current.parent
    return path[::-1]  # Return reversed path


def astar(maze, start, end, allow_diagonal_movement=False):
    """
    Returns as a path from the given start to the given end in the given maze
    :param maze:
    :param start:
    :param end:
    :return: list of tuples
    """

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Heapify the open_list and Add the start node
    heapq.heapify(open_list)
    heapq.heappush(open_list, start_node)

    # what squares do we search
    adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0))
    if allow_diagonal_movement:
        adjacent_squares = (
            (0, -1), (0, 1), (-1, 0), (1, 0),
            (-1, -1), (-1, 1), (1, -1), (1, 1),
        )

    # Loop until you find the end
    while open_list:

        # Get the current node
        current_node = heapq.heappop(open_list)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            return return_path(current_node)

        # Generate children
        children = []

        for new_position in adjacent_squares:  # Adjacent squares

            # Get node position
            node_position = (
                current_node.position[0] + new_position[0],
                current_node.position[1] + new_position[1],
            )

            # Make sure within range
            if (
                node_position[0] > (len(maze) - 1) or
                node_position[0] < 0 or
                node_position[1] > (len(maze[len(maze)-1]) - 1) or
                node_position[1] < 0
            ):
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:
            # Child is on the closed list
            if [
                closed_child
                for closed_child in closed_list
                if closed_child == child
            ]:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = (((child.position[0] - end_node.position[0]) ** 2) +
                       ((child.position[1] - end_node.position[1]) ** 2))
            child.f = child.g + child.h

            # Child is already in the open list
            if [
                open_node
                for open_node in open_list
                if child.position == open_node.position
                and child.g > open_node.g
            ]:
                continue

            # Add the child to the open list
            heapq.heappush(open_list, child)

    return None