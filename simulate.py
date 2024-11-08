
import matplotlib.pyplot as plt
import numpy as np
import random
import statistics

def gamba(percentage):
	if random.random() <= percentage:
		return True
	return False


def simulate():
	player_stage = 0 
	target_stage = 1

	percentage = 0.0
	num_attempts = 0
	while player_stage != target_stage:
		if gamba(percentage):
			player_stage += 1
		if random.random() <= 0.25:
			percentage += 0.0002 * num_attempts
		num_attempts += 1

	return num_attempts


if __name__ == '__main__':
	results = []
	for i in range(100000):
		res = simulate()
		results.append(res)

	print(np.percentile(results, 10))
	print(np.percentile(results, 20))
	print(np.percentile(results, 30))
	print(np.percentile(results, 40))
	print("50th: ", np.percentile(results, 50))
	print(np.percentile(results, 60))
	print(np.percentile(results, 70))
	print(np.percentile(results, 80))
	print(np.percentile(results, 90))

	plt.hist(results, bins=max(results))
	plt.show()