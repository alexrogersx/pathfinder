from Package import Package


class Empty:
    """
    class type to represent an empty bucket
    """
    pass


class HashTable:
    """
    Creates a Quadratic chaining hash table.

    First creates an Empty object that will be used to delineate between 'empty since start' and 'empty due to removal'
    types which will be using in collision avoidance.

    Defaults to a linear search if both c1 and c2 are not specified or set to 0.

    For all insert, search, and remove methods, the worst case complexity is O(N) which happen be when all of the
    buckets are occupied resulting in collisions occurring. This hashtable will almost always run at O(1) since it
    automatically resizes at a set capacity and uses a quadratic chaining algorithm to further reduce collisions.
    """

    def __init__(self, capacity=20, c1=0, c2=0):
        """
        :param capacity: the initial capacity of the hash_table
        :param c1: first constant in quadratic hash function
        :param c2: second constant in quadratic hash function
        """
        self.c1 = c1
        self.c2 = c2
        self.EMPTY_SINCE_START = Empty()
        self.EMPTY_AFTER_REMOVAL = Empty()
        # init table to an empty since start bucket array
        self.data = [self.EMPTY_SINCE_START] * capacity
        self.occupied_buckets = 0

    # implements quadratic search algo
    def quadratic_hash(self, item_id, searched_buckets):
        """
        helper function which hashes the item_id provided with the specified quadratic hash function
        :param item_id: item id to hash
        :param searched_buckets: number of previously searched buckets
        :return: hash value result from function
        """
        hashed = (hash(item_id) + self.c1 * searched_buckets + self.c2 * searched_buckets ** 2) % len(self.data)
        return hashed

    def check_capacity(self):
        """
        checks the amount of occupied buckets, if it is greater than 50% of total capacity, the table is resized to
        twice its previous capacity
        :return: None
        """
        if self.occupied_buckets > len(self.data) * .50:
            temp = self.data
            self.data = [self.EMPTY_SINCE_START] * (len(self.data) * 2)
            item: Package
            for item in filter(lambda x: type(x) is not Empty, temp):
                self.insert(item)

    def insert(self, item):
        """
        Searches for a bucket that is empty and inserts item if found
        if bucket was occupied, search continues until an empty bucket is found or all items have been searched.
        After item is inserted into empty bucket, the occupied_buckets count is incremented and check_capacity() is
        :param item: item to search for
        :return: found item
        """
        searched_buckets = 0
        item_id = item.id
        while searched_buckets < len(self.data):
            current_bucket = self.quadratic_hash(item_id, searched_buckets)
            if type(self.data[current_bucket]) is Empty:
                # bucket was empty therefore we can store our item in it
                self.data[current_bucket] = item
                self.occupied_buckets += 1
                self.check_capacity()
                return True
            # bucket was not empty, will continue searching for next bucket sequence
            searched_buckets += 1
        # table "data" is at its limit
        return False

    def search(self, item_id):
        """
        Searches and removes bucket that matches item
        if bucket was occupied or empty due to removal, search continues until item is found, all items are searched,
        or a bucket is encountered that is empty since start.
        :param item_id: id of item to search for
        :return: found item or None
        """

        searched_buckets = 0
        current_bucket = self.quadratic_hash(item_id, searched_buckets)
        found = None
        while searched_buckets < len(self.data) and self.data[current_bucket] is not self.EMPTY_SINCE_START:
            if type(current_bucket) is not Empty and self.data[current_bucket].id == item_id:
                found = self.data[current_bucket]

            current_bucket = self.quadratic_hash(item_id, searched_buckets)
            searched_buckets += 1

        return found

    def remove(self, item_id):
        """
        Searches and removes bucket that matches item
        if bucket was occupied or empty due to removal, search continues until item is found, all items are searched,
        or a bucket is encountered that is empty since start.
        Once desired item is found, it is removed and the occupied_buckets counter is decremented.
        :param item_id: id of item to remove
        :return: None
        """
        searched_buckets = 0
        current_bucket = self.quadratic_hash(item_id, searched_buckets)

        while searched_buckets < len(self.data) and self.data[current_bucket] is not self.EMPTY_SINCE_START:
            current_bucket = self.quadratic_hash(item_id, searched_buckets)

            if self.data[current_bucket] == item_id:
                self.data[current_bucket] = self.EMPTY_AFTER_REMOVAL
                self.occupied_buckets -= 1

            current_bucket = self.quadratic_hash(item_id, searched_buckets)
            searched_buckets += 1

    def filter_packages(self, function):
        """
        filters data in hash_table based on function
        first removes Empty items that are used only for hash table functionality
        :param function: function to filter data
        :return: filtered data as list
        """
        non_empty_buckets = filter(lambda x: type(x) is not Empty, self.data)
        return list(filter(function, non_empty_buckets))

    def get_all_packages(self):
        """
        :return: all items in hashtable
        """
        return self.filter_packages(lambda x: x)

    def __str__(self):
        """
        converts string representation to something human readable
        """
        i = 0
        spacer = '___________\n'
        for item in self.data:
            s = str(item)
            if item is self.EMPTY_AFTER_REMOVAL:
                s = 'Empty after removal'
            elif item is self.EMPTY_SINCE_START:
                s = 'Empty since start'
            # spacer += "%s %s % (i, s)"
            spacer += "%2d:|   ---|-->%s\n" % (i, s)
            i += 1
        spacer += '____________'
        return spacer
