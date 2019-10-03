import os
import io
from google.cloud import videointelligence
import json
import boto3

class objects:
	
	logger = -1

	def __init__(self,logger,event):
		self.logger = logger.global_log
		credentials = "syn-g-cloud-ac072cf6a455.json"
		result = self.send_video(credentials,self.build_path(event))
		self.process_objects(result)

	def build_path(self,event):
		folder_temporary = '/tmp'
		video_content = event['video-content']
		tmp_video = '{}/{}'.format(folder_temporary, video_content)
		return tmp_video

	def send_video(self,credentials,tmp_video):
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
		
	def process_objects(self,result):
		self.logger.info('OBJECTS')
		object_list = []
		for i, obj in enumerate(result.annotation_results[0].object_annotations):
			if(len(obj.entity.description)>0):
				appearance_list = self.all_appearances(obj.segment.start_time_offset,obj.frames,obj.confidence)
				object_list = self.all_objects(obj.entity.description,appearance_list,object_list)
		self.write_json(object_list)

	def all_appearances(self,initial_time,all_frames,confidence):
		appearance_list = []
		previous_milliseconds = self.milliseconds(initial_time)
		for current_frame in all_frames:
			current_milliseconds = self.milliseconds(current_frame.time_offset)
			appearance_dict = self.one_appearance(current_frame.normalized_bounding_box,
				previous_milliseconds,current_milliseconds,confidence)
			appearance_list.append(appearance_dict)
			previous_milliseconds = current_milliseconds
		return appearance_list

	def milliseconds(self,time):
		milliseconds = str(round((time.seconds + time.nanos/1e9)*1000,4))
		return milliseconds

	def one_appearance(self,box,previous_milliseconds,current_milliseconds,confidence):
		appearance_dict = {}
		appearance_dict["left"] = round(box.left,4)
		appearance_dict["top"] = round(box.top,4)
		appearance_dict["right"] = round(box.right,4)
		appearance_dict["bottom"] = round(box.bottom,4)
		appearance_dict["start"] = previous_milliseconds
		appearance_dict["end"] = current_milliseconds
		appearance_dict["confidence"] = round(confidence,4)
		return appearance_dict		

	def all_objects(self,object_name,appearance_list,object_list):
		exist = self.check_existence(object_list,object_name)
		if exist:
			object_list = self.already_on_list(object_list,object_name,appearance_list)
		else:
			object_list = self.new_on_list(object_list,object_name,appearance_list)
		return object_list

	def check_existence(self,object_list,name):
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
