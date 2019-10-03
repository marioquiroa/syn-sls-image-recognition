from libraries.logger import logger
from libraries.downloader import downloader
from libraries.objects import objects 
from libraries.save_file import save_file 

def main(event, context):
	log = logger(context.aws_request_id)
	downloader(log, event, context)
	o = objects(log, event)
	save_file(log, o.get_json())

if __name__ == "__main__":
	main('', '')
