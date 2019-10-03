from google.cloud import videointelligence
import os
import io

class gcp_service:

	logger = -1
	result = {}

	def __init__(self,logger,event):
		self.logger = logger.global_log
		credentials = "syn-g-cloud-ac072cf6a455.json"
		path = self.build_path(event)
		self.result = self.send_video(credentials,path)

	def build_path(self,event):
		folder_temporary = '/tmp'
		video_content = event['video-content']
		tmp_video = '{}/{}'.format(folder_temporary, video_content)
		return tmp_video

	def send_video(self,credentials,tmp_video):
		self.logger.info('GCP call')
		os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=credentials
		video_client = videointelligence.VideoIntelligenceServiceClient()
		operation = video_client.annotate_video(
			input_content=self.read_video(tmp_video), 
			features=[videointelligence.enums.Feature.OBJECT_TRACKING], 
			location_id='us-east1')
		result = operation.result(timeout=900)
		return result

	def read_video(self,tmp_video):
		with io.open(tmp_video, 'rb') as file:
			input_content = file.read()	
		return input_content

	def get_response(self):
		return self.result