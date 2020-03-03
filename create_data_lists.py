from utils import create_data_lists

def data_ready(data_path):
	create_data_lists(voc07_path=data_path,
                      voc12_path=data_path,
                      output_folder='./')


if __name__ == '__main__':
    create_data_lists(voc07_path='./data',
                      voc12_path='/data',
                      output_folder='./')
