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
		list_objs = []
		for i, obj in enumerate(result.annotation_results[0].object_annotations):
			if(len(obj.entity.description)>0):
				prev_ms = str(round((obj.segment.start_time_offset.seconds + obj.segment.start_time_offset.nanos/1e9)*1000,4))
				list_sub = []
				objects_sub_dict = {}
				for obj_f in obj.frames:
					box = obj_f.normalized_bounding_box
					
					ms_current = str(round((obj_f.time_offset.seconds+obj_f.time_offset.nanos/1e9)*1000,4))
					
					objects_sub_dict["left"] = round(box.left,4)
					objects_sub_dict["top"] = round(box.top,4)
					objects_sub_dict["right"] = round(box.right,4)
					objects_sub_dict["bottom"] = round(box.bottom,4)
					objects_sub_dict["start"] = prev_ms
					objects_sub_dict["end"] = ms_current
					objects_sub_dict["confidence"] = round(obj.confidence,4)
					
					list_sub.append(objects_sub_dict)
					objects_sub_dict = {}

					prev_ms = ms_current
				exist = self.check_existence(list_objs,obj.entity.description)
				if exist:
					list_objs = self.already_on_list(list_objs,obj.entity.description,list_sub)
				else:
					list_objs = self.new_on_list(list_objs,obj.entity.description,list_sub)
		self.write_json(list_objs)

	def check_existence(self,list_objs,name,list_sub):
		exist = False
		for element in list_objs: 
			if(element['object']==name):
				exist = True
				break;	
		return exist

	def already_on_list(self,list_objs,name,list_sub):
		for element in list_objs: 
			if(element['object']==name):
				element['appearances'] += list_sub
				break;
		return list_objs

	def new_on_list(self,list_objs,name,list_sub):
		objects_dict = {}
		objects_dict["object"] = name
		objects_dict["appearances"] = list_sub
		list_objs.append(objects_dict)
		return list_objs

	def write_json(self,list_objs):
		bucket = 'syn-ai-aaoi'
		s3 = boto3.resource("s3").Bucket(bucket)
		json.dump_s3 = lambda obj, f: s3.Object(key='file.json').put(Body=json.dumps(obj))
		json.dump_s3(list_objs,'file.json')
