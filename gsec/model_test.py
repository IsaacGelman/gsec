from model_building.create_model_utils import create_dataframe
from model_building.create_model import create_model
import os

ROOT = os.path.dirname(os.path.realpath(__file__))


def main():
	path = os.path.join(ROOT, "model_building", "data", "1")
	
	df = create_dataframe("/home/cs104/testdata/1","positive","negative",[i for i in range(1, 6+1)])
	create_model(df, 6, "2") != 0


if __name__ == '__main__':
	main()
