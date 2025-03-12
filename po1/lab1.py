
import time
import threading
import random

#генерування масиву випадкових чисел заданого розміру і діапазону значень
def generate_random_array(size, min_val, max_val):
    array = []

    for i in range(size):
        array.append(random.randint(min_val, max_val))

    return array

#звичайне сортування злиттям
def merge_sort(array):
    if len(array) == 1:
        return array
    middle = len(array) // 2
    left = array[:middle]
    right = array[middle:]

    left = merge_sort(left)
    right = merge_sort(right)

    return merge(left, right)

#злиття
def merge(left, right):
    merged = []
    i, j = 0, 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def parallel_merge_sort(array):
    if len(array) <= 1:
        return array
    middle = len(array) // 2
    left = array[:middle]
    right = array[middle:]

    result = [None, None]
    thread1 = threading.Thread(target=threaded_merge_sort, args=(left, result, 0))
    thread2 = threading.Thread(target=threaded_merge_sort, args=(right, result, 1))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    return merge(result[0], result[1])

def threaded_merge_sort(array, result_list, index):
    sorted_part = merge_sort(array)
    result_list[index] = sorted_part

# збереження у файл згенерованого масиву
def save_data(filename, data):
    file = open(filename, "w")
    file.write(" ".join(str(x) for x in data))
    file.close()

# читання масиву з файлу
def read_data(filename):
    file = open(filename, "r")
    data = file.read().split()
    file.close()
    return [int(x) for x in data]

if __name__ == "__main__":
    #налагодження алгоритму для малого масиву
    filename = 'array_0'
    size = 5

    array_0 = generate_random_array(size, 0, 100)
    save_data(filename, array_0)
    data_0 = read_data(filename)

    # Послідовне сортування
    start_time = time.time()

    sorted_array_0_1 = merge_sort(data_0)

    end_time = time.time()
    print(f"\nЧас послідовного сортування для масиву {size}: {end_time - start_time}")
    save_data('sorted_1_array_0', sorted_array_0_1)

    # Паралельне сортування
    start_time = time.time()

    sorted_array_0_2 = parallel_merge_sort(data_0)

    end_time = time.time()
    print(f"Час паралельного сортування для масиву {size}: {end_time - start_time:}")
    save_data('sorted_2_array_0', sorted_array_0_2)

    print(f"Чи однаково відсортовані масиви? {sorted_array_0_1 == sorted_array_0_2}")



    #
    # # виконання алгоритму для великих масивів
    #
    # filename = 'array_1'
    # size = 1000000
    #
    # array_1 = generate_random_array(size, 0, 10000)
    # save_data(filename, array_1)
    # data_1 = read_data(filename)
    #
    # # Послідовне сортування
    # start_time = time.time()
    #
    # sorted_array_1_1 = merge_sort(data_1)
    #
    # end_time = time.time()
    # print(f"\nЧас послідовного сортування для масиву {size}: {end_time - start_time}")
    # save_data('sorted_1_array_1', sorted_array_1_1)
    #
    # # Паралельне сортування
    # start_time = time.time()
    #
    # sorted_array_1_2 = parallel_merge_sort(data_1)
    #
    # end_time = time.time()
    # print(f"Час паралельного сортування для масиву {size}: {end_time - start_time:}")
    # save_data('sorted_2_array_1', sorted_array_1_2)
    # print(f"Чи однаково відсортовані масиви? {sorted_array_1_1 == sorted_array_1_2}")





    # filename = 'array_10'
    # size = 10000000
    #
    # array_10 = generate_random_array(size, 0, 10000)
    # save_data(filename, array_10)
    # data_10 = read_data(filename)
    #
    # # Послідовне сортування
    # start_time = time.time()
    #
    # sorted_array_10_1 = merge_sort(data_10)
    #
    # end_time = time.time()
    # print(f"\nЧас послідовного сортування для масиву {size}: {end_time - start_time}")
    # save_data('sorted_1_array_10',
    #           sorted_array_10_1)
    #
    # # Паралельне сортування
    # start_time = time.time()
    #
    # sorted_array_10_2 = parallel_merge_sort(data_10)
    #
    # end_time = time.time()
    # print(f"Час паралельного сортування для масиву {size}: {end_time - start_time:}")
    # save_data('sorted_2_array_10',
    #           sorted_array_10_2)
    # print(f"Чи однаково відсортовані масиви? {sorted_array_10_1 == sorted_array_10_2}")
    #
