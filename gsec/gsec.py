from .gsec_train import train
from .gsec_apply import predict

def main()
	# do option parsing...
	train = False
	apply_ = False

	if train:
		train()
	elif apply_:
		predict()
	
	return 0


if __name__ == '__main__':
	main()
