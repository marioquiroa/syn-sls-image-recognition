import os
import io
from google.cloud import videointelligence

class label_and_scene:
	
	logger = -1

	def __init__(self,logger,event):
		#variables
		self.logger = logger.global_log
		folder_temporary = 'C:/Temp'
		video_content = event['video-content']
		credentials = "syn-g-cloud-ac072cf6a455.json"
		input_content = ''
		location = 'us-east1'
		#build
		tmp_video = '{}/{}'.format(folder_temporary, video_content)
		os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=credentials
		gcp_feats = videointelligence.enums.Feature
		#open
		with io.open(tmp_video, 'rb') as file:
			input_content = file.read()
		#init the service
		video_client = videointelligence.VideoIntelligenceServiceClient()
		#feats to be called
		features = [gcp_feats.LABEL_DETECTION, gcp_feats.SHOT_CHANGE_DETECTION]
		#call
		operation = video_client.annotate_video(
			input_content=input_content, 
			features=features, 
			location_id=location)
		#result
		result = operation.result(timeout=900)
		#print
		self.get_scenes(result)
		self.get_labels_segment(result)
		self.get_labels_shot(result)		
		
	def get_scenes(self,result):
		self.logger.info('SCENES')
		f = open('scenes.csv','w+')
		for i, shot in enumerate(result.annotation_results[0].shot_annotations):
			start_time = round((shot.start_time_offset.seconds + shot.start_time_offset.nanos / 1e9)*1000,4)
			end_time = round((shot.end_time_offset.seconds + shot.end_time_offset.nanos / 1e9)*1000,4)
			line = '{},{},{}'.format(i, start_time, end_time)
			self.logger.info(line)
			f.writelines(line + '\n')
		f.close()
			

	def get_labels_segment(self,result):
		self.logger.info('LABELS PER SEGEMENT')
		f = open('labels_segment.csv','w+')
		for i, segment_label in enumerate(result.annotation_results[0].segment_label_annotations):
			#time
			start_time = segment_label.segments[0].segment.start_time_offset
			start_ms = str(round((start_time.seconds + start_time.nanos/1e9)*1000,4))
			end_time = segment_label.segments[0].segment.end_time_offset
			end_ms = str(round((end_time.seconds + end_time.nanos/1e9)*1000,4))
			#confidence
			confidence = round(segment_label.segments[0].confidence,4)
			#name
			name_entity = segment_label.entity.description
			#categories
			sub_line = ''
			if(len(segment_label.category_entities)>0):
				for category_entity in segment_label.category_entities:
					sub_line += '{},'.format(category_entity.description)
			#has categories
			if(len(sub_line)>0):
				line = '{},{},{},{},{}'.format(name_entity,confidence,start_ms,end_ms,sub_line[:-1])
			else:
				line = '{},{},{},{}'.format(name_entity,confidence,start_ms,end_ms)
			#print and save
			self.logger.info(line)
			f.writelines(line + '\n')
		f.close()

	def get_labels_shot(self,result):
		self.logger.info('LABELS PER SHOT')
		f = open('labels_shot.csv','w+')
		for i, shot_label in enumerate(result.annotation_results[0].shot_label_annotations):
			#time
			start_time = shot_label.segments[0].segment.start_time_offset
			start_ms = str(round((start_time.seconds + start_time.nanos/1e9)*1000,4))
			end_time = shot_label.segments[0].segment.end_time_offset
			end_ms = str(round((end_time.seconds + end_time.nanos/1e9)*1000,4))
			#confidence
			confidence = round(shot_label.segments[0].confidence,4)
			#name
			name_entity = shot_label.entity.description
			#categories
			sub_line = ''
			if(len(shot_label.category_entities)>0):
				for category_entity in shot_label.category_entities:
					sub_line = '{},'.format(category_entity.description)
			#has categories
			if(len(sub_line)>0):
				line = '{},{},{},{},{}'.format(name_entity,confidence,start_ms,end_ms,sub_line[:-1])
			else:
				line = '{},{},{},{}'.format(name_entity,confidence,start_ms,end_ms)		
			#print and save
			self.logger.info(line)
			f.writelines(line + '\n')
		f.close()