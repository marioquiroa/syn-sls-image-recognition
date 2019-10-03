import json
import boto3

class save_file:

	logger = -1

	def __init__(self,logger,object_list):
		self.logger = logger.global_log
		bucket = 'syn-ai-aaoi'
		s3 = boto3.resource("s3").Bucket(bucket)
		json.dump_s3 = lambda obj, f: s3.Object(key='file.json').put(Body=json.dumps(obj))
		json.dump_s3(object_list,'file.json')
		self.logger.info('Write file')
