from libraries.logger import logger
from libraries.downloader import downloader
from libraries.label_and_scene import label_and_scene 

def main(event, context):
	log = logger(context.aws_request_id)
	downloader(log, event, context)
	label_and_scene(log, event)

if __name__ == "__main__":
	main('', '')