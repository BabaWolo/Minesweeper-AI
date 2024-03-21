import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If amount of cells and count of mines are equal return as the set of known mines
        if len(self.cells) == self.count and self.count > 0:
            return self.cells
        # Return empty set if no known mines
        else: return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If no mines, return the cells as safe
        if self.count == 0:
            return self.cells
        # Return an empty set if no known safe cells
        else: return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # Remove cell if in sentence and update count given cell is a known mine
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # Remove cell if in sentence
        if cell in self.cells:
            self.cells.remove(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Append cell to moves made
        self.moves_made.add(cell)

        # Mark as safe cell
        self.mark_safe(cell)

        # List of undetermined cells which should be added to knowledge
        undetermined_cells = []

        # Check if a cell is undetermined or if cell is a mine reduce count
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Continue loop if current cell
                if (i, j) == cell:
                    continue
                # If a neighbor is a mine reduce count
                elif (i, j) in self.mines:
                    count -= 1
                # Append undetermined cells
                elif 0 <= i < self.height and 0 <= j < self.width and (i, j) not in self.safes and (i, j) not in self.moves_made:
                    undetermined_cells.append((i, j))

        # New sentence with undetermined cells and count 
        new_sentence = Sentence(undetermined_cells, count)

        # Add to new sentence to knowledge
        self.knowledge.append(new_sentence)

        # Check every sentence in the knowledge base
        # If a sentence contains a cell which is not a previously made move, check wether the cell can be determined as safe or mine
        for sentence in self.knowledge:
            if sentence.known_safes():
                for cell in sentence.known_safes().copy():
                    self.mark_safe(cell)
            if sentence.known_mines():
                for cell in sentence.known_mines().copy():
                    self.mark_mine(cell)

        # Check for possible inferences
        while True:
            new_inference_made = False

            # Using subset method to check knowledge for possible inferences
            for sentence in self.knowledge:
                for possible_subset in self.knowledge:
                    if possible_subset.cells.issubset(sentence.cells):
                        if sentence.count != 0 and possible_subset.count != 0 and sentence != possible_subset:
                            new_inference = Sentence(sentence.cells - possible_subset.cells, sentence.count - possible_subset.count)
                            if new_inference not in self.knowledge:
                                self.knowledge.append(new_inference)
                                # Continue while loop in case of new possible inferences
                                new_inference_made = True

            # No inference made, exit while loop                 
            if not new_inference_made:
                break


            

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None


               

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_moves = []
        # Check the entire board pick a random move which hasn't been played nor a mine
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    possible_moves.append((i, j))

        if len(possible_moves) > 0:
            return random.choice(possible_moves)
        else: return None
