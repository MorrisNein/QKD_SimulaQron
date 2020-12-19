import math
import random
import numpy as np
import pandas as pd

ask_block_parity_external = None


def run_cascade(ask_block_parity_function, initial_key_string, qber):
    global ask_block_parity_external
    # This was made to unify the module's use as main and as export.
    # The function is used later in ask_block_parity(...)
    ask_block_parity_external = ask_block_parity_function

    key_block_storage = KeyBlockStorage(initial_key_string)

    cascade(4, key_block_storage, qber)

    return key_block_storage.get_bit_string()


# TODO: Should the class be static?
class KeyBlockStorage:
    """The objects of the class store key"""

    correct_parities_dict = {}

    def __init__(self, initial_key):
        if not isinstance(initial_key, pd.Series):
            initial_key = pd.Series([int(i) for i in initial_key], dtype=int)

        self.key = initial_key
        self.block_positions_by_iterations_dict = {}
        # TODO: optimal parities storage
        # self.correct_block_parities_dict = {}

    def invert_bit(self, position):

        # inverting bit
        value = self.key[position]
        self.key[position] = int(not value)

    def shuffle_block(self, key_block, iteration, qber):
        key_block_len = len(key_block)
        """
        Let k_i is sub-block length on i-th iteration
        k_0 = 0.73 / QBER
        k_(i+1) = k_i * 2
        Then the number of blocks on current iteration:
        n_blocks = key_block_len / k_i
        """
        k_i = round(0.73 / qber) * (2 ** iteration)
        n_blocks = math.ceil(key_block_len / k_i)

        if iteration == 0:
            split_blocks_positions = np.array_split(key_block.index, n_blocks)
        else:
            key_block = key_block.sample(key_block_len)
            split_blocks_positions = np.array_split(key_block.index, n_blocks)

        self.block_positions_by_iterations_dict[iteration] = pd.arrays.SparseArray(split_blocks_positions)

        return self.block_positions_by_iterations_dict[iteration]

    def get_block_num_containing_position(self, iteration, pos):
        iteration_blocks = self.block_positions_by_iterations_dict[iteration]
        for block_num, block_positions in enumerate(iteration_blocks):
            if pos in block_positions:
                return block_num

    def get_bit_string(self):
        return "".join([str(i) for i in self.key])


def cascade(n_iterations, key_blocks_storage, qber):
    """
    Input: RawKey, NumIterations
    Output: CorrectedKey

    for iterationNumber ← 0 to NumIterations do
        iterationBlocks := getIterationBlocks(RawKey, iterationNumber);
        currentBlockParities := calculateParities(iterationBlocks);
        correctBlockParities := askParities(iterationBlocks) ; // Remote function call
        for blockNumber ← 0 to currentBlockParities.length do
            if correctBlockParities[blockNumber] != currentBlockParities[blockNumber] then
                errorIndex := Binary(iterationBlocks[blockNumber]);
                RawKey[errorIndex] := ¬ RawKey[errorIndex];
                cascadeEffect(RawKey, iterationNumber, errorIndex);
            end
        end
    end
    return RawKey;"""

    for i in range(n_iterations):
        key = key_blocks_storage.key

        iteration_blocks = key_blocks_storage.shuffle_block(key, iteration=i, qber=qber)

        parities_correct = [ask_block_parity(block) for block in iteration_blocks]

        for block_num, block in enumerate(iteration_blocks):
            if parities_correct[block_num] != calculate_block_parity(key[block]):
                cascade_effect(i, block_num, key_blocks_storage)

    return key_blocks_storage.key


def cascade_effect(last_cascade_iteration, current_cascade_block_num, key_blocks_storage):
    """Input: RawKey, LastIteration, FirstErrorIndex
    setOfErrorBlocks := PriorityQueue(order by length: crescent);
    currentIteration := LastIteration;
    currentErrorIndex := FirstErrorIndex;
    do
        for iterationNumber ← 0 to LastIteration+1 do
            if iterationNumber != currentIteration then
                block := getCorrespondingBlock(iterationNumber, currentErrorIndex);
                setOfErrorBlocks.append(block);
            end
        end
        errorBlock := setOfErrorBlocks.pop();
        if getParity(errorBlock) != getCorrectParity(errorBlock) then
            currentIteration := errorBlock.iteration;
            currentErrorIndex := Binary(errorBlock);
            RawKey[errorIndex] := ¬ RawKey[errorIndex];
        end
    while setOfErrorBlocks is not empty;"""

    current_iteration = last_cascade_iteration

    errors_to_process = pd.DataFrame(columns=[
        'iteration',
        'block_num',
    ])

    # The initial block to correct error
    errors_to_process.loc[0] = [
        current_iteration,
        current_cascade_block_num
    ]

    while not errors_to_process.empty:
        # Similar to list.pop(0)
        error = errors_to_process.loc[0]
        errors_to_process.drop(index=0, inplace=True)

        block_positions = key_blocks_storage.block_positions_by_iterations_dict[error['iteration']][error['block_num']]

        key_block = key_blocks_storage.key[block_positions]

        parity = calculate_block_parity(key_block)
        parity_correct = ask_block_parity(block_positions)

        if parity_correct != parity:
            current_iteration = error['iteration']
            current_error_position = binary(key_block)
            key_blocks_storage.invert_bit(current_error_position)

            for i in range(last_cascade_iteration + 1):

                if i != current_iteration:
                    block_num = key_blocks_storage.get_block_num_containing_position(i, current_error_position)

                    new_row = {
                        'iteration': i,
                        'block_num': block_num
                    }
                    errors_to_process = errors_to_process.append(new_row, ignore_index=True)

        errors_to_process.sort_values(by="iteration", ascending=True, inplace=True, ignore_index=True)


def binary(key_block):
    """The recursive algorithm finds the first erroneous bit of the block
    with odd number of errors.
    :param key_block: The value of input key block.
    """

    key_block_len = len(key_block)
    # The last recursion level. Return the found error index.
    if key_block_len == 1:
        return key_block.index.tolist()[0]

    l_2 = math.ceil(key_block_len / 2)
    first_half = key_block[:l_2]

    parity_correct = ask_block_parity(first_half.index)  # ask parity of partner's correct key block
    parity = calculate_block_parity(first_half)

    if parity_correct != parity:  # we need to go deeper into the first half
        return binary(first_half)
    else:  # check the second half of current level
        second_half = key_block[l_2:]
        return binary(second_half)


def calculate_block_parity(key_block, key_block_positions=None):
    if isinstance(key_block, str):
        key_block = pd.Series([int(i) for i in key_block])

    if key_block_positions is None:
        parity = sum(key_block) % 2
    else:
        parity = sum(key_block[key_block_positions]) % 2

    return parity


def ask_block_parity(key_block_positions):
    positions_fset = frozenset(key_block_positions)
    if positions_fset in KeyBlockStorage.correct_parities_dict:
        parity = KeyBlockStorage.correct_parities_dict[positions_fset]
    else:
        if callable(ask_block_parity_external):
            parity = ask_block_parity_external(key_block_positions)
        else:
            parity = calculate_block_parity(key_correct[key_block_positions])
        KeyBlockStorage.correct_parities_dict[positions_fset] = parity
    return parity


def get_bit_string(key_block):
    return "".join([str(i) for i in key_block])


def main():
    import time
    global key_correct

    start = time.time()

    key_len = 128
    qber = 0.15

    res = []

    n_monte_karlo = 100

    for _ in range(n_monte_karlo):
        key_correct = pd.Series([random.randint(0, 1) for _ in range(key_len)])

        key = pd.Series([int((random.random() < qber) ^ bool(k)) for k in key_correct])
        key_block_storage = KeyBlockStorage(key)

        cascade(4, key_block_storage, qber)

        result = int(pd.Series(key == key_correct).all())
        res.append(result)

    end = time.time()
    print(f"Time elapsed: {end - start}")

    print(f"Fully successful fraction"
          f" amongst {n_monte_karlo} random keys of length {key_len} with QBER {qber * 100}%"
          f" is {np.round(np.mean(res), 4) * 100}%")


if __name__ == '__main__':
    global key_correct
    main()
