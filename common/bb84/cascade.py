import math
import random
import numpy as np
import pandas as pd

ask_block_parity_external = None


def run_cascade(ask_block_parity_function, initial_key_string, qber):
    global ask_block_parity_external

    ask_block_parity_external = ask_block_parity_function

    key_block_storage = KeyBlockStorage(initial_key_string)

    cascade(4, key_block_storage, qber)

    return key_block_storage.get_bit_string()


class KeyBlockStorage:
    def __init__(self, initial_key):
        if not isinstance(initial_key, pd.Series):
            initial_key = pd.Series([int(i) for i in initial_key], dtype=int)

        self.key = initial_key
        self.block_positions_dict = {}
        # TODO: optimal parities storage
        # self.block_parities_dict = {}

    def invert_bit(self, position):

        # inverting bit
        value = self.key[position]
        self.key[position] = int(not value)

        # inverting parities of blocks that contain that bit
        # TODO: optimal parities storage
        # for i in range(iteration):
        #     for block_num in self.block_parities_dict[i]:
        #         if position in self.block_parities_dict[i][block_num]:
        #             parity = self.block_parities_dict[i][block_num]
        #             self.block_parities_dict[i][block_num] = int(not parity)

    def shuffle_block(self, key_block, iteration, qber):
        key_block_len = len(key_block)
        # Let k_i is block length on i-th iteration
        # k_1 = 0.73 / qber
        # k_i = k_i / 2
        # Then the number of blocks on current iteration:
        # n_blocks = key_block_len / k_i
        k_i = round(0.73 / qber) * 2 ** iteration
        # if iteration == 0:
        #     print(k_i)
        n_blocks = math.ceil(key_block_len / k_i)

        # n_blocks = round(2 ** (iteration+1))
        # print(f"blocks number = {n_blocks}, length = {k_i}")

        if iteration == 0:
            split_blocks_positions = np.array_split(key_block.index, n_blocks)
        else:
            # key_block = key_block.sample(key_block_len, random_state=0)
            key_block = key_block.sample(key_block_len)
            split_blocks_positions = np.array_split(key_block.index, n_blocks)

        self.block_positions_dict[iteration] = pd.arrays.SparseArray(split_blocks_positions)

        # TODO: optimal parities storage
        # parities = \
        #     [calculate_block_parity(self.key[block_positions]) for block_positions in split_blocks_positions]
        # self.block_parities_dict[iteration] = pd.DataFrame(parities).T

        # self.invert_bit(iteration, position=0)
        # print(self.key)
        # exit()
        return self.block_positions_dict[iteration]

    def get_block_num_containing_position(self, iteration, pos):
        iteration_blocks = self.block_positions_dict[iteration]
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

    # not_first_iteration = (n_iterations > 0)  # Can always skip the last block parity after the first iteration
    for i in range(n_iterations):
        key = key_blocks_storage.key

        # print(f"Cascade iteration: {i}, current key: {key_blocks_storage.get_bit_string()}")

        iteration_blocks = key_blocks_storage.shuffle_block(key, iteration=i, qber=qber)

        parities_correct = [ask_block_parity(block) for block in iteration_blocks]

        for block_num, block in enumerate(iteration_blocks):
            if parities_correct[block_num] != calculate_block_parity(key[block]):
                cascade_effect(i, block_num, key_blocks_storage)

    return key_blocks_storage.key


def cascade_effect(last_iter_num, current_block_num, key_blocks_storage):
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

    current_iter_num = last_iter_num
    # current_error_position = first_error_position
    # current_block_num = init_block_num
    errors_to_process = pd.DataFrame(columns=['iteration', 'block_num', 'block_len'])

    errors_to_process.loc[0] = [current_iter_num, current_block_num,
                                len(key_blocks_storage.block_positions_dict[current_iter_num][current_block_num])]

    while not errors_to_process.empty:
        error = errors_to_process.loc[0]
        errors_to_process.drop(index=0, inplace=True)
        block_positions = key_blocks_storage.block_positions_dict[error['iteration']][error['block_num']]

        key_block = key_blocks_storage.key[block_positions]

        parity = calculate_block_parity(key_block)
        parity_correct = ask_block_parity(block_positions)

        if parity_correct != parity:
            current_iter_num = error['iteration']
            current_error_position = binary(key_block)
            key_blocks_storage.invert_bit(current_error_position)

            for i in range(last_iter_num + 1):

                if i != current_iter_num:
                    block_num = key_blocks_storage.get_block_num_containing_position(i, current_error_position)

                    new_row = {'iteration': i,
                               'block_num': block_num,
                               'block_len': len(key_blocks_storage.block_positions_dict[i][block_num])}
                    errors_to_process = errors_to_process.append(new_row, ignore_index=True)

        errors_to_process.sort_values('block_len', ascending=True, inplace=True, ignore_index=True)


def binary(key_block):
    """Input: Block
    Result: ErrorIndex
    if Block.length = 1 then
        return Block.getIndex();
    else
        firstHalf := Block.getSubBlock(0, Block.length / 2);
        correctFirstHalfParity := askBlockParity(firstHalf); // Remote function call
        currentFirstHalfParity := calculateParity(firstHalf);
        if correctFirstHalfParity 6= currentFirstHalfParity then
            return Binary(firstHalf);
        else
            secondHalf := Block.getSubBlock(Block.length / 2, Block.length);
            return Binary(secondHalf);
        end
    end"""

    key_block_len = len(key_block)

    if key_block_len == 1:
        return key_block.index.tolist()[0]
    else:
        l_2 = math.ceil(key_block_len / 2)
        first_half = key_block[:l_2]

        parity_correct = ask_block_parity(first_half.index)  # ask for parity of transmitter's sifted key
        parity = calculate_block_parity(first_half)
    if parity_correct != parity:
        return binary(first_half)
    else:
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
    # TODO: ask for parity from transmitter node
    if callable(ask_block_parity_external):
        return ask_block_parity_external(key_block_positions)
    else:
        return calculate_block_parity(key_correct[key_block_positions])


def get_bit_string(key_block):
    return "".join([str(i) for i in key_block])


if __name__ == '__main__':

    # key_len = 300
    # qber = 0.01
    #
    # key_correct = pd.Series([random.randint(0, 1) for i in range(key_len)])
    # key = pd.Series([int((random.random() < qber) ^ bool(k)) for k in key_correct])
    # blocks = KeyBlockStorage(key)
    # print(f"Correct key: {get_bit_string(key_correct)}")
    # print(f"Initial key: {get_bit_string(key)}")
    # print(f"It is correct? {(key == key_correct).all()}")
    #
    # cascade(4, blocks)
    #
    # print(f"Correct key: {get_bit_string(key_correct)}")
    # print(f"Final key: {get_bit_string(key)}.")
    # print(f"It is correct? {(key == key_correct).all()}")

    import time

    start = time.time()

    key_len = 128
    qber = 0.15

    res = []

    n_monte_karlo = 100

    for _ in range(n_monte_karlo):
        key_correct = pd.Series([random.randint(0, 1) for i in range(key_len)])

        key = pd.Series([int((random.random() < qber) ^ bool(k)) for k in key_correct])
        blocks = KeyBlockStorage(key)

        cascade(4, blocks, qber)

        result = int(pd.Series(key == key_correct).all())
        res.append(result)

    end = time.time()
    print(f"Time elapsed: {end - start}")

    print(f"Fully successful fraction {np.round(np.mean(res), 4) * 100}% "
          f"amongst {n_monte_karlo} random keys of length {key_len} with QBER {qber * 100}%")
