import json
import boto3

class save_file:

	logger = -1

	def __init__(self,logger,object_list,event):
		self.logger = logger.global_log
		bucket = event['bucket-input']
		s3 = boto3.resource("s3").Bucket(bucket)
		file_path = event['file-objects']
		path_arr = file_path.split('/')
		json.dump_s3 = lambda obj, f: s3.Object(key=path_arr[-1]).put(Body=json.dumps(obj))
		json.dump_s3(object_list,path_arr[-1])
		self.logger.info('Write file')
