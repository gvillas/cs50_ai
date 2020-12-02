import sys
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        words_to_remove = set()
        for var in self.crossword.variables:
            for word in self.domains[var]:
                if var.length != len(word):
                    words_to_remove.add(word)
            for words in words_to_remove:
                self.domains[var].remove(words)
            words_to_remove.clear()


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        words_to_remove = set()
        revision = False
        overlap = self.crossword.overlaps[x, y]
        for word_x in self.domains[x]:
            for word_y in self.domains[y]:
                if word_x[overlap[0]] != word_y[overlap[1]]:
                    words_to_remove.add(word_x)
                else:
                    if word_x in words_to_remove:
                        words_to_remove.remove(word_x)
                    break
        for word in words_to_remove:
            self.domains[x].remove(word)
            revision = True
        words_to_remove.clear()
        return revision


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = set()
            for var in self.crossword.variables:
                aux = self.crossword.neighbors(var)
                for y in aux:
                    queue.add((var, y))
        else:
            queue = arcs
        while len(queue) != 0:
            arc = queue.pop()
            x = arc[0]
            y = arc[1]
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in (self.crossword.neighbors(x)):
                    if z == y:
                        continue
                    queue.add((z, x))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        for var in self.crossword.variables:
            if var not in assignment or len(assignment[var]) == 0:
                return False
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        words = list()
        for var in assignment:
            # Check length
            if len(assignment[var]) != var.length:
                return False

            # Check conflicts between neighbors
            if var.direction == 'across':
                neighbors = self.crossword.neighbors(var)
                for neighbor in neighbors:
                    if neighbor in assignment:
                        overlap = self.crossword.overlaps[var, neighbor]
                        if assignment[var][overlap[0]] != assignment[neighbor][overlap[1]]:
                            return False

            words.append(assignment[var])

        # Check if all values are distinct
        if len(words) != len(set(words)):
            return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        domain_values = list(self.domains[var])
        neighbors = self.crossword.neighbors(var)
        order = list()
        for word in domain_values:
            words_to_remove = 0
            for neighbor in neighbors:
                if neighbor not in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    for value in self.domains[neighbor]:
                        if word[overlap[0]] != value[overlap[1]]:
                            words_to_remove += 1
            information = (word, words_to_remove)
            order.append(information)
        order = sorted(order, key=lambda word: word[1])
        sorted_list = list()
        for i in range(len(order)):
            sorted_list.append(order[i][0])

        return sorted_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        order = list()
        for var in self.crossword.variables:
            if var not in assignment:
                words = len(self.domains[var])
                neighbors = len(self.crossword.neighbors(var))
                information = (var, words, neighbors)
                order.append(information)
        order = sorted(order, key=lambda word: (word[1], -word[2]))
        var = order[0][0]
        return var


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # if assigment complete, return
        if self.assignment_complete(assignment):
            return assignment
        # else
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            else:
                assignment[var] = None
        return None



def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
