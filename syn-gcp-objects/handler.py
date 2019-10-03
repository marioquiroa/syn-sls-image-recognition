from libraries.logger import logger
from libraries.downloader import downloader
from libraries.objects import objects 

def main(event, context):
	log = logger(context.aws_request_id)
	downloader(log, event, context)
	objects(log, event)

if __name__ == "__main__":
	main('', '')
