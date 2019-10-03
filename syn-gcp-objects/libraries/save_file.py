import json
import boto3

class save_file:

	logger = -1

	def __init__(self,logger,object_list,event):
		self.logger = logger.global_log
		bucket = event['bucket-input']
		s3 = boto3.resource("s3").Bucket(bucket)
		json.dump_s3 = lambda obj, path: s3.Object(key=path).put(Body=json.dumps(obj))
		json.dump_s3(object_list,event['file-objects'])
		self.logger.info('Write file')
