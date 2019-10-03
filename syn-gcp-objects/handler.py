from libraries.logger import logger
from libraries.downloader import downloader
from libraries.objects import objects 
from libraries.gcp_service import gcp_service 
from libraries.save_file import save_file 

def main(event, context):
	log = logger(context.aws_request_id)
	downloader(log, event, context)
	s = gcp_service(log,event)
	o = objects(log, s.get_response())
	save_file(log, o.get_json(),event)

if __name__ == "__main__":
	main('', '')
