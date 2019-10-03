import os
import io
from google.cloud import videointelligence
import json
import boto3

class objects:
	
	logger = -1

	def __init__(self,logger,event):
		self.logger = logger.global_log
		folder_temporary = '/tmp'
		video_content = event['video-content']
		credentials = "syn-g-cloud-ac072cf6a455.json"
		input_content = '' #
		tmp_video = '{}/{}'.format(folder_temporary, video_content)
		os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=credentials
		with io.open(tmp_video, 'rb') as file:
			input_content = file.read()
		video_client = videointelligence.VideoIntelligenceServiceClient()
		operation = video_client.annotate_video(
			input_content=input_content, 
			features=[videointelligence.enums.Feature.OBJECT_TRACKING], 
			location_id='us-east1')
		result = operation.result(timeout=900)
		self.get_objects(result)
		
	def get_objects(self,result):
		self.logger.info('OBJECTS')
		object_list = []
		for i, obj in enumerate(result.annotation_results[0].object_annotations):
			if(len(obj.entity.description)>0):
				start_time = obj.segment.start_time_offset
				previous_milliseconds = str(round((start_time.seconds + start_time.nanos/1e9)*1000,4))
				
				appearance_list = []
				appearance_dict = {}
				
				for current_frame in obj.frames:
					
					end_time = current_frame.time_offset
					current_millisecons = str(round((end_time.seconds+current_frame.time_offset.nanos/1e9)*1000,4))
					
					box = current_frame.normalized_bounding_box
					appearance_dict["left"] = round(box.left,4)
					appearance_dict["top"] = round(box.top,4)
					appearance_dict["right"] = round(box.right,4)
					appearance_dict["bottom"] = round(box.bottom,4)
					appearance_dict["start"] = previous_milliseconds
					appearance_dict["end"] = current_millisecons
					appearance_dict["confidence"] = round(obj.confidence,4)
					
					appearance_list.append(appearance_dict)
					appearance_dict = {}

					previous_milliseconds = current_millisecons

					object_name = obj.entity.description

				exist = self.check_existence(object_list,object_name)
				if exist:
					object_list = self.already_on_list(object_list,object_name,appearance_list)
				else:
					object_list = self.new_on_list(object_list,object_name,appearance_list)
		self.write_json(object_list)

	def check_existence(self,object_list,name,appearance_list):
		exist = False
		for element in object_list: 
			if(element['object']==name):
				exist = True
				break;	
		return exist

	def already_on_list(self,object_list,name,appearance_list):
		for element in object_list: 
			if(element['object']==name):
				element['appearances'] += appearance_list
				break;
		return object_list

	def new_on_list(self,object_list,name,appearance_list):
		object_dict = {}
		object_dict["object"] = name
		object_dict["appearances"] = appearance_list
		object_list.append(object_dict)
		return object_list

	def write_json(self,object_list):
		bucket = 'syn-ai-aaoi'
		s3 = boto3.resource("s3").Bucket(bucket)
		json.dump_s3 = lambda obj, f: s3.Object(key='file.json').put(Body=json.dumps(obj))
		json.dump_s3(object_list,'file.json')
