class Node:
    def __init__(self, pattern: str, depth: int, edge_value: int | None):
        self.pattern = pattern
        self.children: list[Node] = []
        self.parent: Node | None = None
        self.depth = depth
        self.edge_value = edge_value
        self.invert_index = None
        self.bit_vector: str = None

    def create_invert_index(self, patterns: list[str]):
        if self.depth == 0:
            self.invert_index = "1" * len(patterns)
            return
        invert_index = ""
        idx = self.depth - 1
        value = self.edge_value
        for p in patterns:
            if p[idx].lower() == "x" or p[idx] == str(value):
                invert_index = invert_index + "1"
            else:
                invert_index = invert_index + "0"

        self.invert_index = invert_index

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def update_bit_vector(self):
        b_filter: bin = int(self.parent.bit_vector, base=2)
        b_invert_index: bin = int(self.invert_index, base=2)
        self.bit_vector = bin(b_filter & b_invert_index)[2:]

    @property
    def is_leaf(self):
        return False if "x" in self.pattern else True

    @property
    def bit_vector_ones_count(self):
        return self.bit_vector.count("1")


class MUPTree:
    def __init__(self, num_attributes: int, cardinality_of_attributes: list[int], patterns: list[str]):
        self.depth = num_attributes
        self.cardinality_of_attributes = cardinality_of_attributes
        self.patterns = patterns
        self.root = Node("x" * num_attributes, 0, None)
        self.root.bit_vector = "1" * len(patterns)
        self.__init_children__()

    def __init_children__(self):
        queue = [self.root]
        while len(queue) != 0:
            current_node = queue.pop(0)
            current_node.create_invert_index(patterns=self.patterns)
            if current_node.depth == self.depth:
                continue
            children_count = self.cardinality_of_attributes[current_node.depth]
            for i in range(children_count):
                child = Node(current_node.pattern.replace("x", str(i), 1), current_node.depth + 1, i)
                current_node.add_child(child)
                queue.append(child)

    def get_best_combinations(self) -> list[Node]:
        queue = [self.root]
        best_known_results = []
        max_ones_count = -1
        while len(queue) != 0:
            node = queue.pop()
            if node.bit_vector is None:
                node.update_bit_vector()
            if node.bit_vector_ones_count < max_ones_count:
                continue
            if node.is_leaf:
                if len(best_known_results) == 0:
                    best_known_results.append(node)
                    max_ones_count = best_known_results[0].bit_vector_ones_count
                elif node.bit_vector_ones_count == max_ones_count:
                    best_known_results.append(node)
                elif node.bit_vector_ones_count > max_ones_count:
                    best_known_results.clear()
                    best_known_results.append(node)
                    max_ones_count = best_known_results[0].bit_vector_ones_count
            else:
                queue.extend(node.children)

        return best_known_results
