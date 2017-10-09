from init import pool, children, counter, num, categories, urls

# Init variables
data = []
trees = []

# Close the pool and wait for the work to finish
pool.close()
pool.join()

print('The end')
