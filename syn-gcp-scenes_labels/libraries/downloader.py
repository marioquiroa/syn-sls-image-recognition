import boto3
from botocore.exceptions import ClientError

class downloader:
	
	logger = -1
	bucket = "syn-ai-aaoi"
	tmp_video = ''
	s3_video = ''
	aws_request_id = ''

	def __init__(self, logger, event, context):
		folder_temporary = 'C:/Temp'
		folder_input = "videos"
		#var
		self.logger = logger.global_log
		video_content = event['video-content']
		self.tmp_video = '{}/{}'.format(folder_temporary, video_content)
		self.s3_video  = '{}/{}'.format(folder_input, video_content)
		self.aws_request_id = context.aws_request_id
		self.download_file()

	def download_file(self):
		try:
			self.download_file_correct()
		except ClientError as e:
			self.download_file_error(e)
	
	def download_file_correct(self):
		s3 = boto3.client('s3') 
		self.logger.info("Downloading video... {}".format(self.tmp_video))
		s3.download_file(self.bucket,self.s3_video,self.tmp_video)

	def download_file_error(self,e):
		if e.response['Error']['Code'] == "404":
			msg = "The object s3://{}/{} does not exist.".format(
				self.bucket,self.s3_video)
		else:
			msg = "[{}] {}: {}".format(
				self.aws_request_id,"Boto3 exception not handled",e.response['Error']['Code'])
		
		if(len(msg)>0):
			self.logger.error(msg)
	

