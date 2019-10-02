from logger import logger
from downloader import downloader
from objects import objects 

def main(event, context):
	log = logger(context.aws_request_id)
	downloader(log, event, context)
	objects(log, event)

if __name__ == "__main__":
	main('', '')
